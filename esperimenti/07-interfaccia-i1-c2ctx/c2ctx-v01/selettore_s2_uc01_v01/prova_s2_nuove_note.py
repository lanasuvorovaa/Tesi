#!/usr/bin/env python3
"""Nuovi dati: una chiamata X0+C2+Z per nota, quattro selector replay.
Non legge mai annotazioni gold, non modifica note/calendario/task.
"""
import argparse,csv,hashlib,json,sys,traceback
from datetime import datetime
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path[:0]=[str(BASE/'pipeline_demo'),str(BASE/'pipeline_demo/frozen/xc_z'),str(BASE/'pipeline_demo/frozen/selector')]
from demo_core import analyze_note
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST
from prova_c2 import request_c2,sha,C2
from runtime_support import PORT,URL,find_model,get_json,launch_server,stop_server,wait_server
from selettore_s2 import choose_variant
from replay_diagnostico import VARIANTS

def save_csv(path,rows):
 if not rows:return
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def validated_cases(path):
 raw=json.loads(path.read_text(encoding='utf-8'))
 cases=raw['casi'] if isinstance(raw,dict) else raw
 if not isinstance(cases,list) or not cases:raise ValueError('Dataset vuoto')
 ids=set()
 for case in cases:
  if not all(isinstance(case.get(k),str) and case[k].strip() for k in ('id','nota','reference_datetime')):raise ValueError('id, nota e reference_datetime obbligatori')
  if case['id'] in ids:raise ValueError('ID duplicato')
  datetime.fromisoformat(case['reference_datetime']);ids.add(case['id'])
 return cases

def integrity():
 saved=json.loads((BASE/'FREEZE_S2.json').read_text(encoding='utf-8'))
 for file,hashvalue in saved['sha256'].items():
  if sha(BASE/file)!=hashvalue:raise RuntimeError('File congelato modificato: '+file)
 if hashlib.sha256(C2.encode()).hexdigest()!=saved['prompt_C2_runtime_sha256']:
  raise RuntimeError('Prompt runtime C2 diverso')
 return saved

def compare(case,result):
 records=[{'review_id':case['id']+'__'+c['id'],'scenario_id':case['id'],'candidate_id':c['id'],
   'note_originale':case['nota'],'citazione':c['evidence'],'tipo_predetto':c['kind'],
   'intenzione_predetta':c['intent'],'decisione_sandbox':c['sandbox_gate'],
   'popup_mostrato':'1' if c['selected'] else '0'} for c in result['candidates']]
 rows=[];cand=[]
 row={'caso':case['id'],'nota':case['nota'],'n_frammenti':len(records)}
 for variant in VARIANTS:
  ds,s=choose_variant(records,variant)
  row[variant+'_popup']='SI' if s else 'NO'
  row[variant+'_testo']=s['text'] if s else ''
  row[variant+'_id']=s['candidate_id'] if s else ''
  for d in ds:
   cand.append({'caso':case['id'],'variante':variant,'frammento':d['text'],'candidate_id':d['candidate_id'],
    'kind':d['kind'],'intent':d['intent'],'Z':d['gate_decision'],'eligible':d['eligible'],
    'score':d['score'],'selected':d['new_popup'],'veto':'|'.join(d.get('s2_veto_reasons',[])),
    'ranking':'|'.join(d.get('s2_ranking_reasons',[])),'reasons':'|'.join(d['reject_reasons'])})
 row['valutazione_umana']='';row['commento_revisore']=''
 return row,cand

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--dataset',required=True,type=Path,help='Nuovo JSON con casi, mai usato per sviluppare S2')
 parser.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01')
 args=parser.parse_args()
 frozen=integrity();cases=validated_cases(args.dataset)
 model=find_model('qwen3-1.7b');binary=args.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not binary.exists():raise FileNotFoundError(binary)
 for key,path in [('model_sha256',model),('runtime_sha256',binary)]:
  actual=sha(path)
  if actual!=frozen[key]:raise RuntimeError(key+' differisce dal freeze: '+actual)
 try:get_json(f'http://127.0.0.1:{PORT}/health')
 except Exception:pass
 else:raise RuntimeError('Porta 8091 già occupata')
 out=BASE/'risultati'/('nuove_note_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 out.mkdir(parents=True,exist_ok=False);(out/'dettagli').mkdir()
 (out/'manifest.json').write_text(json.dumps({'configurazione':'X0+C2+Z invariati; varianti S1 S2-V S2-R S2-VR','dataset_sha256':sha(args.dataset),'freeze':frozen,'gold_loaded':False,'model_writes':False,'parameters':{'temperature':0,'seed':42,'max_tokens':350,'context':4096,'ngl':0,'threads':6}},indent=2,ensure_ascii=False),encoding='utf-8')
 notes=[];cand=[];proc,fh=launch_server(binary,model,out/'llama_server.log')
 try:
  serving=wait_server(proc)
  for i,case in enumerate(cases,1):
   print(f'[{i}/{len(cases)}] {case["id"]}',flush=True)
   try:
    def dispatch(params,system,user):
     if system==EXTRACT_X:
      from constrained_api import request_constrained
      return request_constrained(params,system,user)
     if system==CONTRAST:return request_c2(params,user)
     raise RuntimeError('Prompt diverso da X0/C2')
    res=analyze_note(case['nota'],model=serving,url=URL,timeout=240,now=datetime.fromisoformat(case['reference_datetime']),request_fn=dispatch)
    r,cr=compare(case,res);notes.append(r);cand+=cr
    (out/'dettagli'/(case['id']+'.json')).write_text(json.dumps({'case':case,'result':res,'comparison':r,'candidates':cr},ensure_ascii=False,indent=2),encoding='utf-8')
   except Exception as e:
    notes.append({'caso':case['id'],'nota':case['nota'],'n_frammenti':0,'errore':str(e)})
    (out/'dettagli'/(case['id']+'_ERRORE.txt')).write_text(traceback.format_exc(),encoding='utf-8')
   save_csv(out/'confronto_note.csv',notes);save_csv(out/'confronto_candidati.csv',cand)
 finally:stop_server(proc,fh)
 (out/'report.md').write_text('# Confronto S1 / S2 su note nuove\n\nI conteggi dei popup non misurano l’accuratezza: compilare le valutazioni prima della decisione.\n\n'+f'Note elaborate: {len(notes)}\n',encoding='utf-8')
 print('Risultati:',out)
if __name__=='__main__':main()
