"""X2 UC01 v01: validates verbatim atomic action and context spans.
No changes to frozen downstream code. Invalid items are rejected, never silently repaired.
"""
import json
from pathlib import Path

SCHEMA = json.loads((Path(__file__).parent/'schema_x2_v01.json').read_text(encoding='utf-8'))
ROLES = {'time','place','recipient','object_reference','condition','polarity','modality','other'}
RELATIONS = {'before','after','depends_on','contrasts_with'}

# Equivalent subset of the preregistered schema without $ref/prefixItems,
# to avoid grammar incompatibility in llama.cpp's response_format.
SPAN = {'type':'array','items':{'type':'integer'},'minItems':2,'maxItems':2}
CONTEXT = {'type':'object','additionalProperties':False,'required':['quote','span','role'],
           'properties':{'quote':{'type':'string'},'span':SPAN,'role':{'type':'string','enum':sorted(ROLES)}}}
RELATION = {'type':'object','additionalProperties':False,'required':['target_id','type'],
            'properties':{'target_id':{'type':'string'},'type':{'type':'string','enum':sorted(RELATIONS)}}}
ACTION = {'type':'object','additionalProperties':False,'required':['id','action_quote','action_span','context','relations'],
          'properties':{'id':{'type':'string'},'action_quote':{'type':'string'},'action_span':SPAN,
                        'context':{'type':'array','items':CONTEXT},'relations':{'type':'array','items':RELATION}}}
REQUEST_SCHEMA = {'type':'object','additionalProperties':False,'required':['note_id','actions'],
                  'properties':{'note_id':{'type':'string'},'actions':{'type':'array','items':ACTION}}}

def _span_ok(note, span, quote):
 return (isinstance(span,list) and len(span)==2 and all(type(x) is int for x in span)
         and 0 <= span[0] < span[1] <= len(note) and isinstance(quote,str)
         and bool(quote.strip()) and note[span[0]:span[1]] == quote)

def validate_x2(output, note, expected_note_id='N1'):
 """Return (accepted_actions, errors), preserving indexes and contextual references."""
 errors=[];valid=[]
 if not isinstance(output,dict):return [],['OUTPUT_NOT_OBJECT']
 if set(output)!= {'note_id','actions'}:errors.append('ROOT_FIELDS_INVALID')
 if output.get('note_id')!=expected_note_id:errors.append('NOTE_ID_MISMATCH');return [],errors
 actions=output.get('actions')
 if not isinstance(actions,list):return [],errors+['ACTIONS_NOT_ARRAY']
 seen_ids=set();spans=set()
 for idx,a in enumerate(actions):
  code=f'action[{idx}]'
  if not isinstance(a,dict) or set(a)!={'id','action_quote','action_span','context','relations'}:
   errors.append(code+':FIELDS_INVALID');continue
  aid=a['id']
  if not isinstance(aid,str) or not aid.strip() or aid in seen_ids:
   errors.append(code+':ID_INVALID');continue
  seen_ids.add(aid)
  if not _span_ok(note,a['action_span'],a['action_quote']):
   errors.append(code+':ACTION_SPAN_INVALID');continue
  ts=tuple(a['action_span'])
  if ts in spans:errors.append(code+':DUPLICATE_SPAN');continue
  if not isinstance(a['context'],list) or not isinstance(a['relations'],list):
   errors.append(code+':CONTEXT_OR_RELATION_INVALID');continue
  context=[];bad=False
  for j,c in enumerate(a['context']):
   if (not isinstance(c,dict) or set(c)!={'quote','span','role'} or c.get('role') not in ROLES
        or not _span_ok(note,c.get('span'),c.get('quote'))):
    errors.append(f'{code}:CONTEXT[{j}]_INVALID');bad=True;break
   context.append(c)
  if bad:continue
  relations=[]
  for j,r in enumerate(a['relations']):
   if not isinstance(r,dict) or set(r)!={'target_id','type'} or r.get('type') not in RELATIONS or not isinstance(r.get('target_id'),str):
    errors.append(f'{code}:RELATION[{j}]_INVALID');bad=True;break
   relations.append(r)
  if bad:continue
  valid.append({'id':aid,'action_quote':a['action_quote'],'action_span':a['action_span'],
                'context':context,'relations':relations})
  spans.add(ts)
 accepted_ids={a['id'] for a in valid}
 filtered=[]
 for a in valid:
  if any(r['target_id'] not in accepted_ids or r['target_id']==a['id'] for r in a['relations']):
   errors.append(a['id']+':RELATION_TARGET_INVALID');continue
  filtered.append(a)
 return filtered,errors

def project_quotes(actions):
 """Only literal action_quote, no synthetic concatenation. Metadata stays separate."""
 return {'quotes':[a['action_quote'] for a in actions]}
