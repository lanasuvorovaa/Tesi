#!/usr/bin/env python3
"""X0 vs X1: differisce soltanto il prompt di estrazione.
Classificatore C2, replay Z e selettore S2-V della copia congelata.
Il gold non viene letto. Nessuna scrittura su applicazioni o dati utente.
"""
import argparse, csv, hashlib, json, sys, traceback, time
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'selettore_s2_uc01_v01'
sys.path[:0]=[str(BASE),str(BASE/'pipeline_demo'),str(BASE/'pipeline_demo/frozen/xc_z'),str(BASE/'pipeline_demo/frozen/selector')]
import demo_core
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST, stage1_check
from constrained_api import request_constrained, build_request
from run_notes import call_server
from semantic_core_v6 import parse_json
from prova_c2 import request_c2, sha, C2
from runtime_support import PORT, URL, find_model, get_json, launch_server, stop_server, wait_server
from selettore_s2 import choose_variant

X1=(ROOT/'prompt_X1.txt').read_text(encoding='utf-8').strip()
assert X1 and X1 != EXTRACT_X
VARS=('X0','X1')
FIELDS=['caso','nota','variante','n_frammenti','n_candidati','estrazione_raw','quote_validate','errori_estrazione','n_quote_raw','n_quote_validate','n_quote_rifiutate','popup','popup_testo','tipo_popup','intenzione_popup','errori_pipeline','chiamate_modello','tempo_logico_ms','esito_umano_A_P_E_U','note_revisore']
CFIELDS=['caso','variante','candidate_id','evidence','kind','intent','Z_sandbox','Z_actual','eligible','score','selected','reject_reasons']

def save_csv(path, rows, fields):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def read_cases(path):
 data=json.loads(path.read_text(encoding='utf-8'))
 cases=data['casi'] if isinstance(data,dict) else data
 if not isinstance(cases,list) or not cases:raise ValueError('Dataset vuoto')
 if len({c['id'] for c in cases})!=len(cases):raise ValueError('ID duplicati')
 for c in cases:
  if not all(isinstance(c.get(k),str) and c[k].strip() for k in ('id','nota','reference_datetime')):raise ValueError('Campi mancanti')
  d=datetime.fromisoformat(c['reference_datetime'])
  if d.tzinfo is None:raise ValueError('Fuso orario obbligatorio: '+c['id'])
 return cases

def integrity():
 frozen=json.loads((BASE/'FREEZE_S2.json').read_text(encoding='utf-8'))
 for p,exp in frozen['sha256'].items():
  if sha(BASE/p)!=exp:raise RuntimeError('Freeze S2 alterato: '+p)
 if hashlib.sha256(C2.encode()).hexdigest()!=frozen['prompt_C2_runtime_sha256']:
  raise RuntimeError('Prompt C2 runtime non congelato')
 return frozen

def extract_comparison(case, variant, result):
 original=case['nota'];x=result['extraction']
 raw=x.get('json') if isinstance(x.get('json'),dict) else {}
 rawq=raw.get('quotes',[]) if isinstance(raw,dict) else []
 rawq=rawq if isinstance(rawq,list) else []
 q=result['quotes'];validated,err=stage1_check(x.get('json'),original)
 if validated!=q:raise AssertionError('Mismatch quote validate')
 # raw invalid may include duplicates: measure discarded count per output entry, not unique spans
 selected=None;diags=[];recs=[]
 for item in result.get('candidates',[]):
  recs.append({'scenario_id':case['id'],'candidate_id':item['id'],'review_id':case['id']+'__'+item['id'],
   'note_originale':original,'citazione':item['evidence'],'tipo_predetto':item['kind'],
   'intenzione_predetta':item['intent'],'decisione_sandbox':item['sandbox_gate'],
   'popup_mostrato':'1' if item['selected'] else '0'})
 diags,chosen=choose_variant(recs,'S2-V')
 if chosen:
  selected=next((d for d in recs if d['candidate_id']==chosen['candidate_id']),None)
 cr=[]
 for i,d in zip(result['candidates'],diags):
  cr.append({'caso':case['id'],'variante':variant,'candidate_id':i['id'],'evidence':i['evidence'],
             'kind':i['kind'],'intent':i['intent'],'Z_sandbox':i['sandbox_gate'],'Z_actual':i['actual_gate'],
             'eligible':d['eligible'],'score':d['score'],'selected':d['new_popup'],
             'reject_reasons':'|'.join(d['reject_reasons'])})
 row={'caso':case['id'],'nota':original,'variante':variant,'n_frammenti':len(q),
      'n_candidati':len(recs),'estrazione_raw':json.dumps(x.get('json'),ensure_ascii=False),
      'quote_validate':json.dumps(q,ensure_ascii=False),'errori_estrazione':'|'.join(map(str,x.get('errors',[]))),
      'n_quote_raw':len(rawq),'n_quote_validate':len(q),'n_quote_rifiutate':max(0,len(rawq)-len(q)),
      'popup':'SI' if selected else 'NO','popup_testo':selected['citazione'] if selected else '',
      'tipo_popup':selected['tipo_predetto'] if selected else '',
      'intenzione_popup':selected['intenzione_predetta'] if selected else '',
      'errori_pipeline':'|'.join(map(str,result.get('errors',[]))),
      'chiamate_modello':result.get('model_calls'),'tempo_logico_ms':result.get('latency_ms'),
      'esito_umano_A_P_E_U':'','note_revisore':''}
 return row,cr

def request_x1(params, system, user):
 """Transport identical to frozen extraction; only system text X1 changes.
 Build with registered X0 for the schema, then replace ONLY the system message.
 Never alter constrained_api.py or its frozen hash.
 """
 if system != X1:
  raise ValueError('X1 adapter called with unexpected system prompt')
 req = build_request(params.model, EXTRACT_X, user, params.max_tokens)
 assert req['response_format']['json_schema']['name'] == 'atomic_quotes'
 req['messages'][0]['content'] = X1
 begin = time.perf_counter()
 try:
  raw, finish, usage = call_server(params.url, req, params.timeout)
  parsed, err = parse_json(raw)
  return {'raw':raw,'json':parsed,'parse_error':err,'finish_reason':finish,
          'usage':usage,'latency_ms':round((time.perf_counter()-begin)*1000,2),'error':None}
 except Exception as exc:
  return {'raw':None,'json':None,'parse_error':None,'finish_reason':None,
          'usage':{},'latency_ms':round((time.perf_counter()-begin)*1000,2),
          'error':f'{type(exc).__name__}: {exc}'}

def run_one(case, variant, model):
 prompt=EXTRACT_X if variant=='X0' else X1
 def dispatch(params,system,user):
  if system==prompt:
   return request_constrained(params,system,user) if variant=='X0' else request_x1(params,system,user)
  if system==CONTRAST:return request_c2(params,user)
  raise RuntimeError('Modifica inattesa del prompt')
 saved=demo_core.EXTRACT_X
 try:
  demo_core.EXTRACT_X=prompt
  result=demo_core.analyze_note(case['nota'],model=model,url=URL,timeout=240,
                              now=datetime.fromisoformat(case['reference_datetime']),request_fn=dispatch)
 finally:demo_core.EXTRACT_X=saved
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True)
 p.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01')
 p.add_argument('--out',type=Path);a=p.parse_args()
 frozen=integrity();cases=read_cases(a.dataset)
 model=find_model('qwen3-1.7b');binary=a.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not binary.is_file():raise FileNotFoundError(binary)
 for k,path in [('model_sha256',model),('runtime_sha256',binary)]:
  if sha(path)!=frozen[k]:raise RuntimeError('Modello/runtime diverso dal freeze: '+k)
 try:get_json(f'http://127.0.0.1:{PORT}/health')
 except Exception:pass
 else:raise RuntimeError('Porta del server gia occupata')
 out=a.out or ROOT/'risultati'/('x0_vs_x1_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);(out/'dettagli').mkdir()
 manifest={'experiment':'X0 vs X1; C2 + Z + S2-V frozen','dataset_sha256':sha(a.dataset),
           'prompt_X0_sha256':hashlib.sha256(EXTRACT_X.encode()).hexdigest(),
           'prompt_X1_sha256':hashlib.sha256(X1.encode()).hexdigest(),
           'frozen_S2':frozen,'gold_loaded':False,'production_writes':False,
           'note_count':len(cases),'parameters':{'temperature':0,'seed':42,'max_tokens':350,'context':4096,'ngl':0,'threads':6}}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
 rows=[];candidates=[]
 proc,fh=launch_server(binary,model,out/'llama_server.log')
 try:
  serving=wait_server(proc)
  for n,case in enumerate(cases,1):
   for variant in VARS:
    print(f'[{n}/{len(cases)}] {case["id"]} {variant}',flush=True)
    try:
     result=run_one(case,variant,serving)
     r,cr=extract_comparison(case,variant,result);rows.append(r);candidates.extend(cr)
     (out/'dettagli'/f'{case["id"]}_{variant}.json').write_text(json.dumps({'case':case,'variant':variant,'result':result,'evaluation':r,'candidates':cr},ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception as exc:
     rows.append({'caso':case['id'],'nota':case['nota'],'variante':variant,'errori_pipeline':f'{type(exc).__name__}: {exc}'})
     (out/'dettagli'/f'{case["id"]}_{variant}_ERRORE.txt').write_text(traceback.format_exc(),encoding='utf-8')
    save_csv(out/'confronto_estrazioni.csv',rows,FIELDS)
    save_csv(out/'confronto_candidati.csv',candidates,CFIELDS)
 finally:stop_server(proc,fh)
 (out/'report.md').write_text(f'# Esperimento X0 / X1\n\nNote: {len(cases)}; righe varianti: {len(rows)}. Nessuna metrica di accuratezza automatica; compilare la revisione umana.\n',encoding='utf-8')
 print('Risultati:',out)
if __name__=='__main__':main()
