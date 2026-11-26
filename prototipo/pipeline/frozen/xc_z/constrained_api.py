"""Only transport/decoding differs from v01. Prompts and downstream code are frozen."""
import json,time
from run_notes import call_server
from semantic_core_v6 import parse_json
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST

EXTRACTION_SCHEMA={
 'type':'object','properties':{'quotes':{'type':'array','items':{'type':'string'}}},
 'required':['quotes'],'additionalProperties':False
}
CLASSIFICATION_SCHEMA={
 'type':'object',
 'properties':{
  'kind':{'type':'string','enum':['TASK','EVENT','FACT']},
  'intent':{'type':'string','enum':['COMMITTED','TENTATIVE','HYPOTHETICAL','COMPLETED','NEGATED','INFORMATIONAL']}
 },'required':['kind','intent'],'additionalProperties':False
}

def build_request(model, system, user, max_tokens=350):
 if system==EXTRACT_X: name='atomic_quotes'; schema=EXTRACTION_SCHEMA
 elif system==CONTRAST: name='atomic_labels'; schema=CLASSIFICATION_SCHEMA
 else: raise ValueError('Unrecognized system prompt: refusing to change protocol silently')
 return {'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],
  'temperature':0,'seed':42,'max_tokens':max_tokens,'stream':False,
  'chat_template_kwargs':{'enable_thinking':False},
  'response_format':{'type':'json_schema','json_schema':{'name':name,'strict':True,'schema':schema}}}

def request_constrained(args,system,user):
 req=build_request(args.model,system,user,args.max_tokens)
 begin=time.perf_counter()
 try:
  raw,finish,usage=call_server(args.url,req,args.timeout)
  parsed,err=parse_json(raw)
  return {'raw':raw,'json':parsed,'parse_error':err,'finish_reason':finish,'usage':usage,
          'latency_ms':round((time.perf_counter()-begin)*1000,2),'error':None}
 except Exception as exc:
  return {'raw':None,'json':None,'parse_error':None,'finish_reason':None,'usage':{},
          'latency_ms':round((time.perf_counter()-begin)*1000,2),'error':f'{type(exc).__name__}: {exc}'}
