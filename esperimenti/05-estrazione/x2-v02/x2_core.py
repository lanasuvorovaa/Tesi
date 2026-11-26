"""UC-01 X2 v02. Exact-match offset determination without fuzzy repair.

Model supplies literal quotes, Python aligns them to the original note. Ambiguous
repeated substrings and absent text are rejected; context is never synthesized.
"""
from collections import Counter

ROLES={'time','place','recipient','object_reference','condition','polarity','modality','other'}
RELATIONS={'before','after','depends_on','contrasts_with'}
CONTEXT={'type':'object','additionalProperties':False,'required':['quote','role'],
 'properties':{'quote':{'type':'string'},'role':{'type':'string','enum':sorted(ROLES)}}}
RELATION={'type':'object','additionalProperties':False,'required':['target_id','type'],
 'properties':{'target_id':{'type':'string'},'type':{'type':'string','enum':sorted(RELATIONS)}}}
ACTION={'type':'object','additionalProperties':False,'required':['id','action_quote','context','relations'],
 'properties':{'id':{'type':'string'},'action_quote':{'type':'string'},
 'context':{'type':'array','items':CONTEXT},'relations':{'type':'array','items':RELATION}}}
REQUEST_SCHEMA={'type':'object','additionalProperties':False,'required':['note_id','actions'],
 'properties':{'note_id':{'type':'string'},'actions':{'type':'array','items':ACTION}}}

def locate(note, quote):
 """Exactly one literal occurrence; start-inclusive/end-exclusive Python offsets."""
 if not isinstance(quote,str) or not quote or not quote.strip():return None,'EMPTY_QUOTE'
 starts=[];start=0
 while True:
  pos=note.find(quote,start)
  if pos<0:break
  starts.append(pos)
  if len(starts)>1:return None,'AMBIGUOUS_QUOTE'
  start=pos+1
 if not starts:return None,'QUOTE_NOT_FOUND'
 pos=starts[0]
 return [pos,pos+len(quote)],None

def align_x2(output,note,expected_note_id='N1'):
 """Return accepted actions plus item-level error codes; no guessing on repeats.

 Invalid context rejects its action to prevent losing conditions/negation.
 Invalid relationships reject their action to preserve previously frozen semantics.
 """
 errors=[];accepted=[]
 if not isinstance(output,dict):return [],['OUTPUT_NOT_OBJECT']
 if set(output)!={'note_id','actions'}:errors.append('ROOT_FIELDS_INVALID');return [],errors
 if output['note_id']!=expected_note_id:return [],['NOTE_ID_MISMATCH']
 actions=output['actions']
 if not isinstance(actions,list):return [],['ACTIONS_NOT_ARRAY']
 seen_ids=set();seen_spans=set()
 for idx,a in enumerate(actions):
  prefix=f'action[{idx}]'
  if not isinstance(a,dict) or set(a)!={'id','action_quote','context','relations'}:
   errors.append(prefix+':FIELDS_INVALID');continue
  aid=a['id']
  if not isinstance(aid,str) or not aid.strip() or aid in seen_ids:
   errors.append(prefix+':ID_INVALID');continue
  seen_ids.add(aid)
  span,why=locate(note,a['action_quote'])
  if why:errors.append(prefix+':ACTION_'+why);continue
  if tuple(span) in seen_spans:errors.append(prefix+':DUPLICATE_ACTION_SPAN');continue
  if not isinstance(a['context'],list) or not isinstance(a['relations'],list):
   errors.append(prefix+':CONTEXT_OR_RELATIONS_INVALID');continue
  contexts=[];invalid=False
  for j,c in enumerate(a['context']):
   if not isinstance(c,dict) or set(c)!={'quote','role'} or c['role'] not in ROLES:
    errors.append(f'{prefix}:CONTEXT[{j}]_FIELDS_INVALID');invalid=True;break
   cspan,why=locate(note,c['quote'])
   if why:errors.append(f'{prefix}:CONTEXT[{j}]_{why}');invalid=True;break
   contexts.append({'quote':c['quote'],'span':cspan,'role':c['role']})
  if invalid:continue
  relations=[]
  for j,r in enumerate(a['relations']):
   if not isinstance(r,dict) or set(r)!={'target_id','type'} or not isinstance(r['target_id'],str) or r['type'] not in RELATIONS:
    errors.append(f'{prefix}:RELATION[{j}]_INVALID');invalid=True;break
   if r['target_id']==aid:
    errors.append(f'{prefix}:RELATION[{j}]_SELF_REFERENCE');invalid=True;break
   relations.append(dict(r))
  if invalid:continue
  accepted.append({'id':aid,'action_quote':a['action_quote'],'action_span':span,'context':contexts,'relations':relations})
  seen_spans.add(tuple(span))
 # Preserve existing v01 constraint: no dangling relation targets.
 while True:
  valid_ids={a['id'] for a in accepted}
  rejected=[a for a in accepted if any(r['target_id'] not in valid_ids for r in a['relations'])]
  if not rejected:break
  for a in rejected:errors.append(a['id']+':RELATION_TARGET_INVALID')
  accepted=[a for a in accepted if a not in rejected]
 return accepted,errors

def project_quotes(actions):
 return {'quotes':[a['action_quote'] for a in actions]}

def strip_v01_spans(obj):
 """For *offline diagnostic only*: transform stored v01 raw output to v02 format."""
 if not isinstance(obj,dict):return obj
 if not isinstance(obj.get('actions'),list):return obj
 actions=[]
 for a in obj['actions']:
  if not isinstance(a,dict):actions.append(a);continue
  aa={k:v for k,v in a.items() if k!='action_span'}
  if isinstance(aa.get('context'),list):
   aa['context']=[{k:v for k,v in c.items() if k!='span'} if isinstance(c,dict) else c for c in aa['context']]
  actions.append(aa)
 return {**obj,'actions':actions}
