#!/usr/bin/env python3
"""UC-01: confronto appaiato della classificazione C2 legacy vs C2-CTX su X2 congelato.
Nessun cambiamento a X2, C2, Z, S2-V; NON è un test end-to-end.
"""
import argparse,csv,hashlib,json,sys,time,traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'selettore_s2_uc01_v01'
sys.path[:0]=[str(ROOT),str(BASE),str(BASE/'pipeline_demo'),str(BASE/'pipeline_demo/frozen/xc_z'),str(BASE/'pipeline_demo/frozen/selector')]
from prova_c2 import request_c2,sha,C2
from constrained_api import build_request
from run_pipeline_bc import CONTRAST
from run_notes import call_server
from semantic_core_v6 import parse_json
from runtime_support import PORT,URL,find_model,get_json,launch_server,wait_server,stop_server
from valida_interfaccia import validate_document

PROMPT=(ROOT/'prompt_C2_CTX.txt').read_text(encoding='utf8').strip()
SCHEMA={'type':'object','properties':{
 'kind':{'type':'string','enum':['TASK','EVENT','FACT']},
 'intent':{'type':'string','enum':['COMMITTED','TENTATIVE','HYPOTHETICAL','COMPLETED','NEGATED','INFORMATIONAL']},
 'subject_owner':{'type':'string','enum':['SELF','THIRD_PARTY','UNCLEAR']},
 'polarity':{'type':'string','enum':['POSITIVE','NEGATIVE','UNCLEAR']},
 'completion':{'type':'string','enum':['PENDING','DONE','CANCELLED','UNKNOWN']},
 'uncertain':{'type':'boolean'}},'required':['kind','intent','subject_owner','polarity','completion','uncertain'],'additionalProperties':False}
FIELDS=['caso','azione_id','nota','azione','contesti','n_contesti','variante','kind','intent','subject_owner','polarity','completion','uncertain','json_valido','errore','latency_ms','review_kind','review_intent','review_scope','note_revisore']

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def save_csv(path,rows):
 with Path(path).open('w',encoding='utf-8-sig',newline='') as out:
  w=csv.DictWriter(out,fieldnames=FIELDS,extrasaction='ignore');w.writeheader();w.writerows(rows)

def freeze_check():
 frozen=json.loads((BASE/'FREEZE_S2.json').read_text(encoding='utf8'))
 for name,expected in frozen['sha256'].items():
  if sha(BASE/name)!=expected:raise RuntimeError('File congelato alterato: '+name)
 if hashlib.sha256(C2.encode()).hexdigest()!=frozen['prompt_C2_runtime_sha256']:
  raise RuntimeError('Prompt legacy C2 alterato')
 return frozen

def prepare(evidence, dataset):
 raw=json.loads(Path(evidence).read_text(encoding='utf8'))
 notes=json.loads(Path(dataset).read_text(encoding='utf8'))['casi']
 byid={c['case']['id']:c for c in raw['cases']}
 if len(byid)!=len(notes) or set(byid)!={c['id'] for c in notes}:raise ValueError('Mismatch ID tra dataset ed estrazioni congelate')
 document={'schema_version':'I1-v0.1','notes':[]}; flags=[]
 for case in notes:
  original=byid[case['id']]['case']
  if case['nota']!=original['nota'] or case['reference_datetime']!=original['reference_datetime']:
   raise ValueError('Testo/data diversi: '+case['id'])
  if datetime.fromisoformat(case['reference_datetime']).tzinfo is None:raise ValueError('Data senza fuso')
  actions=[]
  for action in byid[case['id']]['accepted']:
   contexts=[]
   for ctx in action.get('context',[]):
    role=ctx['role']
    if role not in {'time','place','recipient','object','polarity','modality','condition','completion','speaker','discourse','antecedent'}:
     flags.append({'caso':case['id'],'azione_id':action['id'],'problema':'ROLE_UNSUPPORTED','role':role});continue
    contexts.append({'quote':ctx['quote'],'span':ctx['span'],'role':role,'scope':[action['id']],
     'source':'explicit_text','confidence_policy':'verified'})
   actions.append({'id':action['id'],'action_evidence':{'quote':action['action_quote'],'span':action['action_span']},
      'context_refs':contexts,'interpretation':None,'provenance':{'extractor':'X2-v02-frozen','version':'I1-adapter-v01'}})
  # Le relazioni X2 sono mantenute soltanto se compatibili con I1, senza correzioni automatiche.
  rel=[]
  for action in byid[case['id']]['accepted']:
   if action.get('relations'):flags.append({'caso':case['id'],'azione_id':action['id'],'problema':'RELATIONS_NOT_PROJECTED'})
  document['notes'].append({'note_id':case['id'],'text':case['nota'],'reference_datetime':case['reference_datetime'],
                           'actions':actions,'relations':rel})
 # La verifica sintattica non certifica la correttezza della portata semantica.
 validate_document(document)
 return document,flags

def user_c2(note,action):
 return 'CONTESTO E FRAMMENTO (dati):\n'+json.dumps({'note':note,'fragment':action['action_evidence']['quote']},ensure_ascii=False)

def user_ctx(note,action):
 return 'AZIONE E CONTESTO (solo dati):\n'+json.dumps({'note':note,'action_id':action['id'],
   'action_evidence':action['action_evidence'],'context_refs':action['context_refs'],
   'relations':[],'scope_note':'scope assegnato da X2, da verificare semanticamente'},ensure_ascii=False)

def request_ctx(args,user):
 # Lo schema di risposta C2-CTX è nuovo; non modifica il builder congelato.
 body=build_request(args.model,CONTRAST,user,args.max_tokens)
 body['messages'][0]['content']=PROMPT
 body['response_format']['json_schema']={'name':'context_labels','strict':True,'schema':SCHEMA}
 start=time.perf_counter()
 try:
  raw,finish,usage=call_server(args.url,body,args.timeout)
  parsed,error=parse_json(raw)
  return {'raw':raw,'json':parsed,'parse_error':error,'finish_reason':finish,'usage':usage,
          'latency_ms':round((time.perf_counter()-start)*1000,2),'error':None}
 except Exception as exc:
  return {'raw':None,'json':None,'parse_error':None,'finish_reason':None,'usage':{},
          'latency_ms':round((time.perf_counter()-start)*1000,2),'error':f'{type(exc).__name__}: {exc}'}

def valid(payload,mode):
 if not isinstance(payload,dict):return False
 if mode=='C2':return set(payload)=={'kind','intent'} and payload['kind'] in SCHEMA['properties']['kind']['enum'] and payload['intent'] in SCHEMA['properties']['intent']['enum']
 if set(payload)!=set(SCHEMA['required']):return False
 for k,v in payload.items():
  rule=SCHEMA['properties'][k]
  if k=='uncertain':
   if type(v)!=bool:return False
  elif v not in rule['enum']:return False
 return True

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--offline-only',action='store_true');ap.add_argument('--dataset',type=Path,default=ROOT/'note_test40_DIAGNOSTICO.json');ap.add_argument('--evidence',type=Path,default=ROOT/'estrazioni_x2_congelate.json');ap.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01');ap.add_argument('--out',type=Path);a=ap.parse_args()
 frozen=freeze_check();doc,flags=prepare(a.evidence,a.dataset)
 out=a.out or ROOT/'risultati'/('c2_ctx_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);(out/'dettagli').mkdir()
 write(out/'interfaccia_I1.json',doc);write(out/'flags_contratto.json',flags)
 write(out/'manifest.json',{'experiment':'C2 vs C2-CTX paired classification only','independent_holdout':False,
   'gold_loaded':False,'writes_performed':False,'Z_and_S_applied':False,
   'input_evidence_sha256':digest(a.evidence),'dataset_sha256':digest(a.dataset),
   'new_prompt_sha256':digest(ROOT/'prompt_C2_CTX.txt'),'new_runner_sha256':digest(__file__),
   'frozen':frozen,'note_count':len(doc['notes']),'flags':len(flags),'offline_only':a.offline_only,
   'caveat':'I1 portata dei contesti ereditata da X2 non verificata semanticamente; relazioni non proiettate'})
 if a.offline_only:
  print('Audit I1:',len(doc['notes']),'note;',sum(len(x['actions']) for x in doc['notes']),'azioni; flags',len(flags));print('Output:',out);return
 model=find_model('qwen3-1.7b');binary=a.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not binary.is_file():raise FileNotFoundError(binary)
 for k,p in [('model_sha256',model),('runtime_sha256',binary)]:
  if sha(p)!=frozen[k]:raise RuntimeError('Hash non compatibile: '+k)
 try:get_json(f'http://127.0.0.1:{PORT}/health')
 except Exception:pass
 else:raise RuntimeError('Porta locale già occupata; impossibile garantire un server isolato')
 rows=[];proc=None;fh=None
 try:
  proc,fh=launch_server(binary,model,out/'llama_server.log');model_id=wait_server(proc)
  args=SimpleNamespace(model=model_id,url=URL,max_tokens=350,timeout=240)
  total=sum(len(x['actions']) for x in doc['notes']);count=0
  for note in doc['notes']:
   for action in note['actions']:
    count+=1
    for mode in ('C2','C2-CTX'):
     print(f'[{count}/{total}] {note["note_id"]} {action["id"]} {mode}',flush=True)
     try:
      user=user_c2(note['text'],action) if mode=='C2' else user_ctx(note['text'],action)
      r=request_c2(args,user) if mode=='C2' else request_ctx(args,user)
      answer=r.get('json') or {};ok=valid(answer,mode)
      row={'caso':note['note_id'],'azione_id':action['id'],'nota':note['text'],
        'azione':action['action_evidence']['quote'],'contesti':json.dumps(action['context_refs'],ensure_ascii=False),
        'n_contesti':len(action['context_refs']),'variante':mode,'kind':answer.get('kind',''),
        'intent':answer.get('intent',''),'subject_owner':answer.get('subject_owner',''),
        'polarity':answer.get('polarity',''),'completion':answer.get('completion',''),
        'uncertain':answer.get('uncertain',''),'json_valido':int(ok),
        'errore':r.get('error') or r.get('parse_error') or ('' if ok else 'INVALID_SCHEMA'),
        'latency_ms':r.get('latency_ms'),'review_kind':'','review_intent':'','review_scope':'','note_revisore':''}
      write(out/'dettagli'/f'{note["note_id"]}_{action["id"]}_{mode}.json',{'input':user,'result':r,'valid':ok})
     except Exception as exc:
      row={'caso':note['note_id'],'azione_id':action['id'],'variante':mode,'errore':f'{type(exc).__name__}: {exc}'}
      (out/'dettagli'/f'{note["note_id"]}_{action["id"]}_{mode}_ERROR.txt').write_text(traceback.format_exc(),encoding='utf8')
     rows.append(row);save_csv(out/'confronto_classificazioni.csv',rows)
 finally:
  if proc:stop_server(proc,fh)
 write(out/'report.json',{'notes':len(doc['notes']),'classified_rows':len(rows),
   'by_variant':{v:{'rows':sum(r['variante']==v for r in rows),
                    'schema_valid':sum(r['variante']==v and r.get('json_valido')==1 for r in rows)} for v in ('C2','C2-CTX')},
   'warning':'Valutazione semantica umana necessaria; non è un test popup end-to-end'})
 print('Output:',out)
if __name__=='__main__':main()
