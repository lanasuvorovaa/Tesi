#!/usr/bin/env python3
"""UC-01: confronto I1 originale vs I1-R manuale, stesso C2-CTX v01.
Non esegue estrazione, C2 legacy, Z, S né scritture sull'app.
"""
import argparse,csv,hashlib,json,sys,time,traceback
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from prova_c2_ctx import (freeze_check,user_ctx,request_ctx,valid,write,save_csv,digest,
  find_model,sha,PORT,URL,get_json,launch_server,wait_server,stop_server,
  PROMPT,SCHEMA)
from valida_interfaccia import validate_document

def verify_pair(a,b):
 validate_document(a);validate_document(b)
 if len(a['notes'])!=40 or len(b['notes'])!=40:raise ValueError('Expected 40 notes')
 ca=cb=0; changed=[]
 for n,m in zip(a['notes'],b['notes']):
  if any(n[k]!=m[k] for k in ('note_id','text','reference_datetime')):raise ValueError('Note changed')
  if n['relations']!=m['relations']:raise ValueError('Relations changed')
  if len(n['actions'])!=len(m['actions']):raise ValueError('Action count changed')
  for x,y in zip(n['actions'],m['actions']):
   if x['id']!=y['id'] or x['action_evidence']!=y['action_evidence']:raise ValueError('Action evidence changed')
   ca+=1;cb+=1
   if x['context_refs']!=y['context_refs']:changed.append((n['note_id'],x['id']))
 if ca!=39 or cb!=39:raise ValueError(f'Expected 39 actions, found {ca} {cb}')
 return changed

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--offline-only',action='store_true')
 parser.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01')
 parser.add_argument('--out',type=Path)
 a=parser.parse_args()
 original=ROOT/'interfaccia_I1_ORIGINALE.json'; revised=ROOT/'interfaccia_I1_R_REVISIONATA.json'
 doc0=json.loads(original.read_text(encoding='utf-8')); doc1=json.loads(revised.read_text(encoding='utf-8'))
 changed=verify_pair(doc0,doc1)
 frozen=freeze_check()
 from prova_c2_ctx import prepare
 prepared,_=prepare(ROOT/'estrazioni_x2_congelate.json',ROOT/'note_test40_DIAGNOSTICO.json')
 # Check that original I1 exactly matches the frozen adapter result from X2.
 if prepared!=doc0:raise RuntimeError('Original I1 differs from frozen X2 adapter output')
 out=a.out or ROOT/'risultati'/('i1_vs_i1r_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);(out/'dettagli').mkdir()
 write(out/'manifest.json',{'experiment':'I1 original vs I1-R manually annotated, C2-CTX v01 frozen',
   'n_notes':40,'n_actions':39,'modified_actions':len(changed),
   'input_original_sha256':digest(original),'input_revised_sha256':digest(revised),
   'prompt_ctx_sha256':hashlib.sha256(PROMPT.encode()).hexdigest(),
   'runner_sha256':digest(__file__),'original_C2_CTX_runner_sha256':digest(ROOT/'prova_c2_ctx.py'),
   'changed_action_ids':changed,'freeze':frozen,'offline_only':a.offline_only,'gold_loaded':False,
   'writes_performed':False,'Z_or_S_applied':False,
   'limitations':'Previously seen synthetic notes; manual correction; unchanged X2 errors cannot be recovered'})
 if a.offline_only:
  print('OK: 40 note, 39 azioni identiche,',len(changed),'azioni con contesti revisionati.')
  print('Output:',out)
  return
 model=find_model('qwen3-1.7b');binary=a.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not binary.is_file():raise FileNotFoundError(binary)
 for k,p in [('model_sha256',model),('runtime_sha256',binary)]:
  if sha(p)!=frozen[k]:raise RuntimeError('Hash non compatibile: '+k)
 try:get_json(f'http://127.0.0.1:{PORT}/health')
 except Exception:pass
 else:raise RuntimeError('Porta locale già occupata, impossibile garantire server isolato')
 proc=fh=None;rows=[];total=39;count=0
 fields=['caso','azione_id','nota','azione','variante','contesti','n_contesti','kind','intent',
         'subject_owner','polarity','completion','uncertain','json_valido','errore','latency_ms']
 try:
  proc,fh=launch_server(binary,model,out/'llama_server.log');model_id=wait_server(proc)
  args=SimpleNamespace(model=model_id,url=URL,max_tokens=350,timeout=240)
  for n0,n1 in zip(doc0['notes'],doc1['notes']):
   for act0,act1 in zip(n0['actions'],n1['actions']):
    count+=1
    for variant,act in [('I1',act0),('I1-R',act1)]:
     print(f'[{count}/{total}] {n0["note_id"]} {act["id"]} {variant}',flush=True)
     row={'caso':n0['note_id'],'azione_id':act['id'],'nota':n0['text'],
          'azione':act['action_evidence']['quote'],'variante':variant,
          'contesti':json.dumps(act['context_refs'],ensure_ascii=False),'n_contesti':len(act['context_refs'])}
     try:
      payload=user_ctx(n0['text'],act)
      response=request_ctx(args,payload)
      answer=response.get('json') or {}
      ok=valid(answer,'C2-CTX')
      row.update({k:answer.get(k,'') for k in ['kind','intent','subject_owner','polarity','completion','uncertain']})
      row.update({'json_valido':int(ok),'errore':response.get('error') or response.get('parse_error') or ('' if ok else 'INVALID_SCHEMA'),'latency_ms':response.get('latency_ms')})
      write(out/'dettagli'/f'{n0["note_id"]}_{act["id"]}_{variant}.json',{'input':payload,'result':response,'valid':ok})
     except Exception as exc:
      row.update({'json_valido':0,'errore':f'{type(exc).__name__}: {exc}'})
      (out/'dettagli'/f'{n0["note_id"]}_{act["id"]}_{variant}_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
     rows.append(row)
     with (out/'confronto_classificazioni.csv').open('w',encoding='utf-8-sig',newline='') as f:
      w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 finally:
  if proc:stop_server(proc,fh)
 write(out/'report.json',{'n_notes':40,'n_actions':39,'outputs':len(rows),
    'by_variant':{v:{'rows':sum(r['variante']==v for r in rows),'valid':sum(r['variante']==v and r.get('json_valido')==1 for r in rows)} for v in ('I1','I1-R')},
    'warning':'Accuracy and regressions require manual semantic review, not an end-to-end test'})
 print('Risultati:',out)
if __name__=='__main__':main()
