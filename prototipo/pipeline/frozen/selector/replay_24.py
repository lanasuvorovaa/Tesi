#!/usr/bin/env python3
"""Frozen selector applied to ALL candidates of 24 archived Qwen3-1.7B X+Z records.
No inference, no gold in selection; never re-enable candidates blocked by Z.
"""
import argparse,csv,hashlib,json,zipfile,collections,pathlib
from frozen_selector import analyze
BASE=pathlib.Path(__file__).resolve().parent
SOURCE=BASE/'data'/'XCZ_constrained_results.zip'
PREFIX='runs/qwen17_constrained/XZ/'
FIELDS=['scenario_id','candidate_id','review_id','note_originale','citazione','testo_candidato','tipo_predetto','intenzione_predetta','decisione_sandbox','popup_mostrato']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load():
 with zipfile.ZipFile(SOURCE) as z:
  names=sorted(x for x in z.namelist() if x.startswith(PREFIX) and x.endswith('.json'))
  if len(names)!=24:raise ValueError('Expected 24 complete XZ results, got '+str(len(names)))
  out=[]
  for name in names:
   rec=json.loads(z.read(name));sid=rec['scenario_id']
   scenario=json.loads((BASE/'data/scenarios'/(sid+'.json')).read_text(encoding='utf-8'))
   note=scenario['input']['text'];pred=rec['converted_output'];evidence={e['evidence_id']:e for e in pred['evidence']}
   gates={x['candidate_id']:x for x in rec['gates']['sandbox']['candidates']}
   candidate_ids={x['candidate_id'] for x in pred['candidates']}
   if candidate_ids!=set(gates):raise ValueError('candidate/gate mismatch '+sid)
   old_id=rec['gates']['sandbox']['single_popup_candidate_id']
   if old_id is not None and old_id not in candidate_ids:raise ValueError('bad prior popup '+sid)
   rows=[]
   for c in pred['candidates']:
    cid=c['candidate_id'];quotes=[evidence[eid]['quote'] for eid in c['evidence_ids']]
    if len(quotes)!=1:raise ValueError('Expected one evidence quote per candidate; refusing to merge: '+sid+' '+cid)
    q=quotes[0]; gate=gates[cid]
    r={'scenario_id':sid,'candidate_id':cid,'review_id':sid+'__'+cid,'note_originale':note,'citazione':q,'testo_candidato':c['canonical_text'],'tipo_predetto':c['kind'],'intenzione_predetta':c['intent_status'],'decisione_sandbox':gate['decision'],'popup_mostrato':str(int(old_id==cid))}
    rows.append(r)
   out.append((rec,rows))
 return out

def choose(rows):
 # IMPORTANT: existing Z gate is authoritative; analyze() cannot re-enable it.
 diagnostic=[]
 for r in rows:
  d=analyze(r)
  d['gate_decision']=r['decisione_sandbox']
  d['eligible']=bool(d['eligible'] and r['decisione_sandbox'] in ('PROPOSE','CLARIFY'))
  if r['decisione_sandbox'] not in ('PROPOSE','CLARIFY'):d['reject_reasons']=sorted(set(d['reject_reasons']+['PREVIOUS_GATE_BLOCKED']))
  diagnostic.append(d)
 feasible=[d for d in diagnostic if d['eligible']]
 chosen=sorted(feasible,key=lambda d:(-d['score'],d['candidate_id']))[0] if feasible else None
 return diagnostic,chosen

def gold_action(c):
 if c.get('kind') not in ('TASK','EVENT'):return None
 return {'COMMITTED':'PROPOSE','TENTATIVE':'CLARIFY'}.get(c.get('intent_status'))
def normalize(s):
 import re,unicodedata
 s=unicodedata.normalize('NFKD',s.lower());s=''.join(ch for ch in s if not unicodedata.combining(ch))
 return set(re.findall(r'[a-z0-9]+',s)) - {'la','il','lo','le','i','gli','un','una','di','da','a','al','alla','e','per','devo','deve','domani','entro','vorrei','potrei'}
def approx_match(row,gold,gevidence):
 if row['tipo_predetto']!=gold['kind'] or row['intenzione_predetta']!=gold['intent_status']:return False
 if row['decisione_sandbox']!=gold_action(gold):return False
 candidate=normalize(row['testo_candidato']+' '+row['citazione']);goal=normalize(gold['canonical_text'])
 if not goal or not candidate:return False
 # Approximate lexical correspondence only; requires human review for semantic correctness
 return len(candidate&goal)/len(goal)>=0.60 and len(candidate&goal)/len(candidate)>=0.35

def main():
 a=argparse.ArgumentParser();a.add_argument('--out',default=str(BASE/'results'));args=a.parse_args()
 dest=pathlib.Path(args.out);dest.mkdir(parents=True,exist_ok=True)
 source=load();candidate_out=[];note_out=[];popup_out=[];summary=collections.Counter();gold_count=0;gold_matched_old=set();gold_matched_new=set()
 for rec,rows in source:
  sid=rec['scenario_id'];ds,selected=choose(rows)
  before=next((r for r in rows if r['popup_mostrato']=='1'),None)
  after=next((r for r in rows if selected and r['review_id']==selected['review_id']),None)
  gold=json.loads((BASE/'data/gold_private'/(sid+'.json')).read_text(encoding='utf-8'))['gold']
  golds=[x for x in gold['candidates'] if gold_action(x)]
  gold_count+=len(golds)
  old_match=next((g['candidate_id'] for g in golds if before and approx_match(before,g,gold['evidence'])),None)
  new_match=next((g['candidate_id'] for g in golds if after and approx_match(after,g,gold['evidence'])),None)
  if old_match:gold_matched_old.add((sid,old_match))
  if new_match:gold_matched_new.add((sid,new_match))
  for d in ds:
   d['selected_new']=bool(selected and d['review_id']==selected['review_id'])
   d['gold_matching_for_diagnostics_only']=next((g['candidate_id'] for g in golds if approx_match(next(r for r in rows if r['review_id']==d['review_id']),g,gold['evidence'])),None)
   candidate_out.append(d)
  row={'scenario_id':sid,'note_originale':rows[0]['note_originale'] if rows else json.loads((BASE/'data/scenarios'/(sid+'.json')).read_text())['input']['text'], 'total_candidates':len(rows),'Z_allowed_candidates':sum(r['decisione_sandbox'] in ('PROPOSE','CLARIFY') for r in rows), 'gold_actionable':len(golds),'old_popup_id':before['review_id'] if before else '', 'old_popup_text':before['citazione'] if before else '', 'new_popup_id':after['review_id'] if after else '', 'new_popup_text':after['citazione'] if after else '', 'old_gold_match_heuristic':old_match or '', 'new_gold_match_heuristic':new_match or '', 'old_popup_exists':bool(before),'new_popup_exists':bool(after),'change':('UNCHANGED' if (before or {}).get('review_id')==(after or {}).get('review_id') else 'REPLACED' if before and after else 'SUPPRESSED' if before else 'NEW' if after else 'NONE'), 'missing_gold_after_new_heuristic':len(golds)-int(bool(new_match))}
  note_out.append(row)
  for position,r,gid in [('BEFORE',before,old_match),('AFTER',after,new_match)]:
   if r: popup_out.append({'scenario_id':sid,'position':position,'review_id':r['review_id'],'text':r['citazione'],'kind':r['tipo_predetto'],'intent':r['intenzione_predetta'],'decision':r['decisione_sandbox'],'heuristic_gold_id':gid or '', 'needs_human_review':True})
  summary['candidates']+=len(rows);summary['notes']+=1;summary['Z_allowed']+=row['Z_allowed_candidates'];summary['old_popups']+=bool(before);summary['new_popups']+=bool(after);summary['changed_notes']+=row['change'] not in ('UNCHANGED','NONE');summary['notes_no_popup_new']+=not bool(after);summary['notes_no_candidates']+=not bool(rows);summary['notes_no_Z_allowed']+=not bool(row['Z_allowed_candidates']);summary['old_popups_heuristic_matched']+=bool(old_match);summary['new_popups_heuristic_matched']+=bool(new_match)
 def csv_save(name,vals):
  with (dest/name).open('w',newline='',encoding='utf-8-sig') as f:
   if not vals:return
   keys=list(vals[0]);w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
   for v in vals:w.writerow({k: '|'.join(str(t) for t in x) if isinstance(x,list) else x for k,x in v.items()})
 csv_save('all_candidates_diagnostics.csv',candidate_out);csv_save('all_24_notes.csv',note_out);csv_save('popups_before_after.csv',popup_out)
 results={'protocol':'frozen-selector-full24-offline-v0.1','source':'original Qwen3-1.7B constrained X+Z run, all 24 development notes','model_calls':0,'persistent_writes':0,'selector_sha256':sha(BASE/'frozen_selector.py'),'source_zip_sha256':sha(SOURCE),'gold_not_used_in_selection':True,'previous_Z_blocks_preserved':True,'preliminary_gold_action_opportunities':gold_count,'heuristic_distinct_gold_matched_before':len(gold_matched_old),'heuristic_distinct_gold_matched_after':len(gold_matched_new),'heuristic_opportunities_missed_after':gold_count-len(gold_matched_new),'metrics':dict(summary),'limitations':['24 development notes used during selector design, so in-sample; no generalization inference','heuristic lexical gold matching is not independent human adjudication','one popup maximum per note: candidate opportunities cannot all be shown','Z blocked candidates are never eligible for selection; potential missed opportunities can originate upstream','human review required for popup correctness and whether blank output is appropriate','task/event capability assumed available only in original sandbox; no write API']}
 (dest/'summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
