#!/usr/bin/env python3
"""Controlled diagnostic X0/X1/X2; frozen C2+Z+S2-V; raw structured X2 and projection traced.
X2 is a compound extraction + projection interface change; not a single-prompt comparison.
"""
import argparse,csv,hashlib,json,sys,traceback,time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'selettore_s2_uc01_v01'
sys.path[:0]=[str(ROOT),str(BASE),str(BASE/'pipeline_demo'),str(BASE/'pipeline_demo/frozen/xc_z'),str(BASE/'pipeline_demo/frozen/selector')]
import demo_core
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST
from constrained_api import build_request
from run_notes import call_server
from semantic_core_v6 import parse_json
from prova_c2 import request_c2,sha
from runtime_support import PORT,URL,find_model,get_json,launch_server,stop_server,wait_server
from prova_x0_x1 import read_cases,integrity,run_one,extract_comparison,save_csv,FIELDS,CFIELDS
from x2_core import REQUEST_SCHEMA,validate_x2,project_quotes
from selettore_s2 import choose_variant

X2=(ROOT/'prompt_X2.txt').read_text(encoding='utf-8').strip()
VARS=('X0','X1','X2')
X2_EXTRA=['x2_raw','x2_actions_accepted','x2_validation_errors','x2_accepted_count','x2_raw_count','x2_context_count','x2_projection_notes']

def request_x2(params,system,user,case,trace):
 if system!=X2:raise ValueError('Unexpected X2 prompt')
 req=build_request(params.model,EXTRACT_X,user,params.max_tokens)
 req['messages'][0]['content']=X2
 req['response_format']={'type':'json_schema','json_schema':{'name':'x2_atomic_actions','strict':True,'schema':REQUEST_SCHEMA}}
 start=time.perf_counter()
 try:
  raw,finish,usage=call_server(params.url,req,params.timeout)
  parsed,err=parse_json(raw)
  accepted,validation=validate_x2(parsed,case['nota'])
  projection=project_quotes(accepted)
  trace.update({'raw':parsed,'accepted':accepted,'validation_errors':validation,'parse_error':err,'raw_text':raw})
  return {'raw':raw,'json':projection,'parse_error':err,'finish_reason':finish,'usage':usage,'latency_ms':round((time.perf_counter()-start)*1000,2),'error':None}
 except Exception as exc:
  trace.update({'raw':None,'accepted':[],'validation_errors':[f'X2_RUNTIME_ERROR: {type(exc).__name__}: {exc}']})
  return {'raw':None,'json':{'quotes':[]},'parse_error':None,'finish_reason':None,'usage':{},'latency_ms':round((time.perf_counter()-start)*1000,2),'error':f'{type(exc).__name__}: {exc}'}

def run_x2(case,model):
 trace={}
 def dispatch(params,system,user):
  if system==X2:return request_x2(params,system,user,case,trace)
  if system==CONTRAST:return request_c2(params,user)
  raise RuntimeError('Unexpected downstream prompt; protocol freeze violation')
 before=demo_core.EXTRACT_X
 try:
  demo_core.EXTRACT_X=X2
  result=demo_core.analyze_note(case['nota'],model=model,url=URL,timeout=240,now=datetime.fromisoformat(case['reference_datetime']),request_fn=dispatch)
 finally:demo_core.EXTRACT_X=before
 return result,trace

def main():
 p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,default=ROOT/'note_test40_DIAGNOSTICO.json');p.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01');p.add_argument('--out',type=Path);a=p.parse_args()
 frozen=integrity();cases=read_cases(a.dataset)
 model=find_model('qwen3-1.7b');binary=a.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not binary.is_file():raise FileNotFoundError(binary)
 for k,path in [('model_sha256',model),('runtime_sha256',binary)]:
  if sha(path)!=frozen[k]:raise RuntimeError('Model/runtime changed: '+k)
 try:get_json(f'http://127.0.0.1:{PORT}/health')
 except Exception:pass
 else:raise RuntimeError('llama-server port already occupied')
 out=a.out or ROOT/'risultati'/('x0_x1_x2_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);(out/'dettagli').mkdir()
 manifest={'experiment':'X0/X1/X2 diagnostic; C2 Z S2-V frozen','comparison_nature':'X2 changes extraction schema and its projection; downstream frozen',
           'dataset_sha256':sha(a.dataset),'prompts_sha256':{'X0':hashlib.sha256(EXTRACT_X.encode()).hexdigest(),
            'X1':sha(ROOT/'prompt_X1.txt'),'X2':sha(ROOT/'prompt_X2.txt')},'schema_x2_sha256':sha(ROOT/'schema_x2_v01.json'),
           'x2_core_sha256':sha(ROOT/'x2_core.py'),'runner_sha256':sha(Path(__file__)),
           'freeze_S2':frozen,'gold_loaded':False,'production_writes':False,'note_count':len(cases),
           'params':{'temperature':0,'seed':42,'max_tokens':350,'context':4096,'ngl':0,'threads':6}}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 rows=[];candidate_rows=[];proc,fh=launch_server(binary,model,out/'llama_server.log')
 try:
  serving=wait_server(proc)
  for n,case in enumerate(cases,1):
   for variant in VARS:
    print(f'[{n}/{len(cases)}] {case["id"]} {variant}',flush=True)
    try:
     if variant=='X2':
      result,trace=run_x2(case,serving)
     else:
      result=run_one(case,variant,serving);trace={}
     row,cands=extract_comparison(case,variant,result)
     if variant=='X2':
      accepted=trace.get('accepted',[])
      row.update({'x2_raw':json.dumps(trace.get('raw'),ensure_ascii=False),'x2_actions_accepted':json.dumps(accepted,ensure_ascii=False),
                  'x2_validation_errors':'|'.join(trace.get('validation_errors',[])),
                  'x2_accepted_count':len(accepted),
                  'x2_raw_count':len((trace.get('raw') or {}).get('actions',[])) if isinstance(trace.get('raw'),dict) else 0,
                  'x2_context_count':sum(len(x['context']) for x in accepted),
                  'x2_projection_notes':'Only literal action quotes passed to frozen C2 and Z; contextual metadata not transferred'})
     rows.append(row);candidate_rows.extend(cands)
     (out/'dettagli'/f'{case["id"]}_{variant}.json').write_text(json.dumps({'case':case,'variant':variant,'result':result,'structured_x2':trace,'evaluation':row,'candidates':cands},ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception as exc:
     rows.append({'caso':case['id'],'nota':case['nota'],'variante':variant,'errori_pipeline':f'{type(exc).__name__}: {exc}'})
     (out/'dettagli'/f'{case["id"]}_{variant}_ERRORE.txt').write_text(traceback.format_exc(),encoding='utf-8')
    save_csv(out/'confronto_estrazioni.csv',rows,FIELDS+X2_EXTRA)
    save_csv(out/'confronto_candidati.csv',candidate_rows,CFIELDS)
 finally:stop_server(proc,fh)
 (out/'report.md').write_text(f'# Diagnostica X0/X1/X2\n\nCasi: {len(cases)}; righe: {len(rows)}. I numeri di popup non sono metriche di accuratezza.\nX2 usa una proiezione letterale che non trasferisce il contesto a C2/Z.\n',encoding='utf-8')
 print('Risultati:',out)
if __name__=='__main__':main()
