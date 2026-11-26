#!/usr/bin/env python3
"""Repeatability of identical C2-CTX inputs. No modification of model/prompt/inputs."""
import argparse,csv,hashlib,json,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
from types import SimpleNamespace
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from prova_c2_ctx import (freeze_check,user_ctx,request_ctx,valid,write,digest,
    find_model,sha,PORT,URL,get_json,launch_server,wait_server,stop_server,PROMPT,SCHEMA)
from valida_interfaccia import validate_document
from prova_i1r import verify_pair
FIELDS=['caso','azione_id','round','order','input_sha256','kind','intent','subject_owner',
        'polarity','completion','uncertain','json_valido','errore','latency_ms']
LABELS=['kind','intent','subject_owner','polarity','completion','uncertain']
def h(s):return hashlib.sha256(s.encode('utf8')).hexdigest()
def samples(doc0,doc1,scope):
 revised={ (n['note_id'],a['id']) for n,m in zip(doc0['notes'],doc1['notes']) for a,b in zip(n['actions'],m['actions']) if a['context_refs']!=b['context_refs'] }
 controls={('UC01-S2TEST-011','a1'),('UC01-S2TEST-002','a1')}
 pairs=[]
 for n in doc1['notes']:
  for a in n['actions']:
   k=(n['note_id'],a['id'])
   if scope=='all' or k in revised or k in controls:
    pairs.append((n,a,'revised' if k in revised else 'control'))
 assert len(revised)==18, f'Expected 18 changed actions, got {len(revised)}'
 if scope=='focus':assert len(pairs)==20, len(pairs)
 return pairs,revised

def csvwrite(path,rows,fields):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def summarize(rows,pairs,repeats):
 by=defaultdict(list)
 for row in rows:by[(row['caso'],row['azione_id'])].append(row)
 summaries=[]
 for n,a,group in pairs:
  key=(n['note_id'],a['id']); rr=by[key]
  good=[r for r in rr if r['json_valido']==1]
  sig=[tuple(str(r.get(k,'')) for k in LABELS) for r in good]
  disagree={k:len(set(str(r.get(k,'')) for r in good)) for k in LABELS}
  summaries.append({'caso':key[0],'azione_id':key[1],'gruppo':group,'ripetizioni':len(rr),
   'valide':len(good),'identico_tutte_le_volte':int(len(good)==repeats and len(set(sig))==1),
   'configurazioni_distinte':len(set(sig)),
   **{'valori_distinti_'+k:disagree[k] for k in LABELS},
   'json_risposte':json.dumps([{k:r.get(k,'') for k in LABELS} for r in rr],ensure_ascii=False)})
 return summaries

def main():
 p=argparse.ArgumentParser();p.add_argument('--repeats',type=int,default=3);p.add_argument('--scope',choices=['focus','all'],default='focus')
 p.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01');p.add_argument('--out',type=Path);p.add_argument('--offline-only',action='store_true')
 args=p.parse_args();assert 2<=args.repeats<=10
 p0=ROOT/'interfaccia_I1_ORIGINALE.json';p1=ROOT/'interfaccia_I1_R_REVISIONATA.json'
 d0=json.loads(p0.read_text(encoding='utf8'));d1=json.loads(p1.read_text(encoding='utf8'))
 changed=verify_pair(d0,d1);frozen=freeze_check();pairs,_=samples(d0,d1,args.scope)
 # Ensures original reconstructed from X2 has not been touched
 from prova_c2_ctx import prepare
 restored,_=prepare(ROOT/'estrazioni_x2_congelate.json',ROOT/'note_test40_DIAGNOSTICO.json')
 if restored!=d0:raise RuntimeError('Original I1 mismatch')
 # Full reproducible user payloads generated in advance, independent of prediction
 payloads={(n['note_id'],a['id']):user_ctx(n['text'],a) for n,a,_ in pairs}
 out=args.out or ROOT/'risultati'/('ripetibilita_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);(out/'dettagli').mkdir()
 schedule=[]
 for rep in range(1,args.repeats+1):
  # Alternate order to detect order-related effects; identical input per action in all rounds
  ordered=pairs if rep%2==1 else list(reversed(pairs))
  for idx,(n,a,group) in enumerate(ordered,1):
   schedule.append({'caso':n['note_id'],'azione_id':a['id'],'round':rep,'order':idx,
                    'input_sha256':h(payloads[n['note_id'],a['id']]),'gruppo':group})
 csvwrite(out/'programma_esecuzione.csv',schedule,list(schedule[0]))
 write(out/'manifest.json',{'experiment':'C2-CTX v01 repeatability on identical I1-R user inputs',
   'scope':args.scope,'n_actions':len(pairs),'repeats':args.repeats,'n_requests':len(schedule),
   'modified_actions_in_source':len(changed),'parameters':{'temperature':0,'seed':42,'max_tokens':350,'context':4096,'ngl':0,'threads':6},
   'prompt_sha256':h(PROMPT),'schema_sha256':h(json.dumps(SCHEMA,sort_keys=True)),
   'input_I1_R_sha256':digest(p1),'input_I1_sha256':digest(p0),'runner_sha256':digest(__file__),
   'original_ctx_runner_sha256':digest(ROOT/'prova_c2_ctx.py'), 'frozen':frozen,
   'model_inference':not args.offline_only,'gold_loaded':False,'Z_or_S_applied':False,'writes_performed':False,
   'warning':'Known synthetic cases; repeated identical input is a stability diagnostic, not gold accuracy. No inference if offline-only.'})
 if args.offline_only:
  print('OK',len(pairs),'azioni,',len(schedule),'richieste pianificate; input identici per azione');print('Output:',out);return
 model=find_model('qwen3-1.7b'); binary=args.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not binary.is_file():raise FileNotFoundError(binary)
 for k,pth in [('model_sha256',model),('runtime_sha256',binary)]:
  if sha(pth)!=frozen[k]:raise RuntimeError('Frozen hash mismatch '+k)
 try:get_json('http://127.0.0.1:%d/health'%PORT)
 except Exception:pass
 else:raise RuntimeError('Port %d occupied'%PORT)
 proc=fh=None;rows=[]
 try:
  proc,fh=launch_server(binary,model,out/'llama_server.log');model_id=wait_server(proc)
  cargs=SimpleNamespace(model=model_id,url=URL,max_tokens=350,timeout=240)
  for i,item in enumerate(schedule,1):
   case,action=item['caso'],item['azione_id'];payload=payloads[(case,action)]
   print(f'[{i}/{len(schedule)}] {case} {action} round {item["round"]}',flush=True)
   row={k:item[k] for k in ['caso','azione_id','round','order','input_sha256']}
   try:
    result=request_ctx(cargs,payload);ans=result.get('json') or {};ok=valid(ans,'C2-CTX')
    row.update({k:ans.get(k,'') for k in LABELS})
    row.update({'json_valido':int(ok),'errore':result.get('error') or result.get('parse_error') or ('' if ok else 'INVALID_SCHEMA'),
                'latency_ms':result.get('latency_ms')})
    write(out/'dettagli'/f'{case}_{action}_r{item["round"]}.json',{'input':payload,'input_sha256':h(payload),'response':result,'schema_valid':ok})
   except Exception as e:
    row.update({'json_valido':0,'errore':type(e).__name__+': '+str(e)})
    (out/'dettagli'/f'{case}_{action}_r{item["round"]}_ERROR.txt').write_text(traceback.format_exc(),encoding='utf8')
   rows.append(row);csvwrite(out/'ripetizioni.csv',rows,FIELDS)
 finally:
  if proc:stop_server(proc,fh)
 summaries=summarize(rows,pairs,args.repeats)
 summaryfields=[k for k in summaries[0]]
 csvwrite(out/'sintesi_per_azione.csv',summaries,summaryfields)
 stable=sum(s['identico_tutte_le_volte'] for s in summaries)
 valid_count=sum(r['json_valido']==1 for r in rows)
 write(out/'report.json',{'requested':len(schedule),'received':len(rows),'valid':valid_count,
  'actions':len(pairs),'stable_all_six_attributes':stable,'unstable_or_invalid':len(pairs)-stable,
  'attribute_variability':{k:sum(s['valori_distinti_'+k]>1 for s in summaries) for k in LABELS},
  'caveat':'A non-identical response on same input shows instability, not necessarily wrong semantics; manual review required.'})
 print('Risultati:',out)
if __name__=='__main__':main()
