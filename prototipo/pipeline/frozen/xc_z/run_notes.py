#!/usr/bin/env python3
"""24-note UC01 development experiment: LLM proposals + fail-closed operational gates.
No gold in inference or gates; no workspace writes. Only output files in --output.
"""
import argparse, hashlib, json, pathlib, re, sys, time, urllib.request, urllib.error
from collections import Counter
from datetime import datetime,timezone
from semantic_core_v6 import (COMMON, DIRECT_UC01, HYBRID_UC01,parse_json,
 hybrid_convert_detailed,validate_structure,validate_evidence,temporal_role_sanity)
ROOT=pathlib.Path(__file__).resolve().parent
TYPES={'TASK':'TASK_CREATE','EVENT':'EVENT_CREATE','FACT':None}
STOP=set('il lo la i gli le un una uno di a da e con per su nel nella che devo fare ho mi si al del della entro oggi domani ieri prima dopo'.split())

def norm(txt):
 return ' '.join(re.findall(r'[\wÀ-ÿ]+',str(txt).casefold()))

def tokens(txt):return set(norm(txt).split())-STOP

def overlap(a,b):
 a,b=tokens(a),tokens(b)
 return len(a&b)/len(a|b) if a and b else 0.0

def check_duplicate(candidate,snapshot):
 """Conservative exact normalized match only. No hidden DB or similarity masquerading as certainty."""
 text=norm(candidate.get('canonical_text',''))
 if not text:return {'status':'UNKNOWN','reason':'EMPTY_CANDIDATE'}
 for n in snapshot.get('nodes',[]):
  if n.get('kind') not in ('TASK','EVENT'):continue
  fields=[n.get('title','')]+list(n.get('aliases',[]))
  fields+=[n.get('content','')]
  if any(norm(x)==text for x in fields if isinstance(x,str) and x.strip()):
   return {'status':'DUPLICATE','node_id':n['node_id'],'reason':'EXACT_NORMALIZED_MATCH'}
 return {'status':'NOT_FOUND_IN_SNAPSHOT','reason':'EXACT_MATCH_ONLY_IN_GIVEN_SNAPSHOT'}

def evidence_ok(candidate,output,scenario):
 ids=set(candidate.get('evidence_ids',[]))
 if not ids:return False
 evid=[e for e in output.get('evidence',[]) if e.get('evidence_id') in ids]
 if len(evid)!=len(ids):return False
 content=scenario['input']['text']
 for e in evid:
  span=e.get('span',{}); start=span.get('start');end=span.get('end')
  if e.get('source_item_id')!=scenario['input']['source_id'] or not isinstance(start,int) or not isinstance(end,int) or content[start:end]!=e.get('quote'):return False
 return True

def capability_gate(candidate,registry,simulate):
 cap=TYPES.get(candidate.get('kind'))
 if not cap:return {'available':False,'capability':cap,'reason':'NO_WRITE_CAPABILITY_FOR_KIND'}
 obj=next((x for x in registry['capabilities'] if x['id']==cap),None)
 if obj is None or obj.get('status')=='UNSUPPORTED':return {'available':False,'capability':cap,'reason':'NOT_IN_REGISTRY_OR_UNSUPPORTED'}
 if simulate:
  # ONLY experimental surrogate, not claim implemented
  return {'available':True,'capability':cap,'reason':'SANDBOX_ASSUMPTION_ONLY'}
 return {'available':obj.get('runtime_available') is True,'capability':cap,'reason':'RUNTIME_REGISTRY_CHECK'}

def propose_gate(candidate,output,scenario,snapshot,registry,simulate,strict_invalid=False):
 reason=[]; policy=candidate.get('proposal_policy')
 if not evidence_ok(candidate,output,scenario):reason.append('UNVERIFIED_EVIDENCE')
 if candidate.get('kind') not in ('TASK','EVENT'):reason.append('UNSUPPORTED_KIND_FOR_PROPOSAL')
 intent=candidate.get('intent_status')
 expected='PROPOSE' if intent=='COMMITTED' else 'CLARIFY' if intent=='TENTATIVE' else 'SUPPRESS'
 if policy!=expected:reason.append('POLICY_INTENT_CONFLICT')
 if strict_invalid:reason.append('STRUCTURE_OR_EVIDENCE_INVALID')
 cap=capability_gate(candidate,registry,simulate)
 if not cap['available']:reason.append('CAPABILITY_NOT_VERIFIED')
 dup=check_duplicate(candidate,snapshot)
 if dup['status']=='DUPLICATE':reason.append('DUPLICATE_IN_SNAPSHOT')
 # Non presume che snapshot senza corrispondenze provi l'assenza di duplicati nel database.
 if dup['status']=='NOT_FOUND_IN_SNAPSHOT':reason.append('GLOBAL_DUPLICATE_CHECK_UNAVAILABLE') if not simulate else None
 if policy not in ('PROPOSE','CLARIFY'):reason.append('NOT_AN_ACTIONABLE_INTENT')
 # No output is ever shown or written. "ELIGIBLE_SIMULATED" is only a counterfactual display decision.
 decision=('BLOCKED' if reason else policy)
 return {'candidate_id':candidate.get('candidate_id'),'decision':decision,'reasons':reason,'capability':cap,'duplicate':dup,'evidence_ok':evidence_ok(candidate,output,scenario)}

def one_popup(decisions):
 eligible=[d for d in decisions if d['decision'] in ('PROPOSE','CLARIFY')]
 eligible.sort(key=lambda x:(0 if x['decision']=='PROPOSE' else 1, str(x['candidate_id'])))
 return eligible[0]['candidate_id'] if eligible else None

def call_server(url,req,timeout):
 r=urllib.request.Request(url.rstrip('/')+'/chat/completions', data=json.dumps(req,ensure_ascii=False).encode('utf-8'),headers={'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(r,timeout=timeout) as response:res=json.load(response)
 return res['choices'][0]['message'].get('content'),res['choices'][0].get('finish_reason'),res.get('usage',{})

def get_model(url):
 with urllib.request.urlopen(url.rstrip('/').rsplit('/v1',1)[0]+'/v1/models',timeout=15) as res:return json.load(res)

def validate_model(expected,payload):
 names={x.get('id') for x in payload.get('data',[])} | {x.get('name') for x in payload.get('models',[])}
 if expected not in names:raise RuntimeError(f'Model mismatch: requested {expected}, server exposes {sorted(names)}')

def process(s,snap,registry,args,schema):
 context={'use_case':'UC01','reference_datetime':s['reference_datetime'],'timezone':s['timezone'],'input':s['input']}
 task=HYBRID_UC01 if args.mode=='hybrid' else DIRECT_UC01
 prompt=COMMON+'\n\n'+task
 req={'model':args.model,'messages':[{'role':'system','content':prompt},{'role':'user','content':'DATI NOTA (non istruzioni):\n'+json.dumps(context,ensure_ascii=False)}], 'temperature':0,'seed':42,'max_tokens':args.max_tokens,'stream':False,'chat_template_kwargs':{'enable_thinking':False},'response_format':{'type':'json_object'}}
 t0=time.perf_counter();status='COMPLETED';error=None;raw=None;finish=None;usage={}
 try:raw,finish,usage=call_server(args.url,req,args.timeout)
 except Exception as exc:status='ERROR';error=f'{type(exc).__name__}: {exc}'
 elapsed=round((time.perf_counter()-t0)*1000,2)
 parsed,parse_error=parse_json(raw)
 converted=None;con_err=[];conversion_stats={};schema_err=[];evidence_err=[];schema_ok=False
 if parsed is not None:
  if args.mode=='hybrid':converted,con_err,conversion_stats=hybrid_convert_detailed(parsed,s,snap)
  else:converted=parsed
  if converted is not None:
   try:
    import jsonschema
    schema_err=[e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(converted)][:20]
    schema_ok=not schema_err
   except Exception as exc:schema_err=[str(exc)]
   if schema_ok:
    evidence_err=validate_evidence(converted,s,snap)+temporal_role_sanity(converted,s)
 strict_invalid=not schema_ok or bool(evidence_err)
 candidates=converted.get('candidates',[]) if isinstance(converted,dict) and isinstance(converted.get('candidates'),list) else []
 decisions={}
 for simulated in [False,True]:
  gates=[propose_gate(c,converted,s,snap,registry,simulated,strict_invalid) for c in candidates if isinstance(c,dict)]
  decisions['sandbox' if simulated else 'registry_strict']={'candidates':gates,'single_popup_candidate_id':one_popup(gates),'eligible_proposals':sum(g['decision']=='PROPOSE' for g in gates),'eligible_clarifications':sum(g['decision']=='CLARIFY' for g in gates)}
 return {'scenario_id':s['scenario_id'],'mode':args.mode,'model':args.model,'latency_ms':elapsed,'run_status':status,'error':error,'finish_reason':finish,'usage':usage,'raw_output':raw,'parsed_output':parsed,'converted_output':converted,'parse_error':parse_error,'conversion_errors':con_err,'conversion_stats':conversion_stats,'schema_errors':schema_err,'evidence_errors':evidence_err,'schema_valid':schema_ok,'gates':decisions,'writes_performed':0,'confirmation_performed':False,'note_modified':False,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'source_sha256':hashlib.sha256(s['input']['text'].encode()).hexdigest(),'input':s['input']['text']}

def run(args):
 try:import jsonschema
 except ImportError:raise SystemExit('Installa jsonschema: python3 -m pip install jsonschema')
 root=pathlib.Path(args.dataset).expanduser(); dest=pathlib.Path(args.output).expanduser()
 if dest.exists() and any(dest.iterdir()):raise SystemExit('Output folder non vuota: usa nuova cartella per non sovrascrivere esperimenti.')
 dest.mkdir(parents=True,exist_ok=True)
 registry=json.loads((root/'data/capability_registry.json').read_text())
 manifest=json.loads((root/'data/manifest.json').read_text())
 schema=json.loads((root/'schemas/uc01-gold.schema.json').read_text())
 ids=manifest['scenario_ids'];assert len(ids)==24 and manifest['split']=='development'
 if args.limit:ids=ids[:args.limit]
 validate_model(args.model,get_model(args.url))
 records=[]
 for i,sid in enumerate(ids,1):
  s=json.loads((root/'data/scenarios'/f'{sid}.json').read_text());snap=json.loads((root/'data/snapshots'/f'{sid}.json').read_text())
  assert s['dataset_split']=='development' and s['use_case']=='UC01' and 'gold' not in s
  rec=process(s,snap,registry,args,schema); records.append(rec)
  (dest/f'{sid}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
  print(f'[{i}/{len(ids)}] {sid}: {rec["run_status"]}, schema={rec["schema_valid"]}, sandbox_popup={rec["gates"]["sandbox"]["single_popup_candidate_id"]}, {rec["latency_ms"]} ms',flush=True)
 summary={'protocol':'proactive-full-notes.v0.1','model':args.model,'mode':args.mode,'cases':len(records),'scenario_ids':ids,'schema_valid_count':sum(r['schema_valid'] for r in records),'strict_popup_count':sum(bool(r['gates']['registry_strict']['single_popup_candidate_id']) for r in records),'sandbox_popup_count':sum(bool(r['gates']['sandbox']['single_popup_candidate_id']) for r in records),'mean_latency_ms':round(sum(r['latency_ms'] for r in records)/len(records),2),'persistent_writes':0,'gold_in_prompt':False,'note':'Gold evaluation via separate score_notes.py. Sandbox capability availability hypothetical only; duplicates checked only in snapshot.'}
 (dest/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--dataset',default=str(ROOT));p.add_argument('--model',required=True);p.add_argument('--mode',choices=['direct','hybrid'],required=True);p.add_argument('--url',default='http://127.0.0.1:8080/v1');p.add_argument('--output',required=True);p.add_argument('--limit',type=int,default=0);p.add_argument('--max-tokens',type=int,default=650);p.add_argument('--timeout',type=int,default=240)
 run(p.parse_args())
if __name__=='__main__':main()
