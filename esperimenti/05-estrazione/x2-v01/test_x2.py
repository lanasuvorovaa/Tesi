import unittest,json
from pathlib import Path
from x2_core import validate_x2,project_quotes,REQUEST_SCHEMA
from prova_x0_x1 import integrity,read_cases

class TestX2(unittest.TestCase):
 def setUp(self):
  self.note='Domani devo pagare il bollo e inviare la ricevuta alla contabilità.'
 def action(self,q,context=None,aid='a1',relations=None):
  p=self.note.index(q)
  return {'id':aid,'action_quote':q,'action_span':[p,p+len(q)],'context':context or [],'relations':relations or []}
 def test_multiple_atomic(self):
  a=self.action('devo pagare il bollo',aid='a1')
  b=self.action('inviare la ricevuta alla contabilità',aid='a2')
  v,e=validate_x2({'note_id':'N1','actions':[a,b]},self.note)
  self.assertEqual(len(v),2);self.assertEqual(e,[])
  self.assertEqual(len(project_quotes(v)['quotes']),2)
 def test_context_exact(self):
  c={'quote':'Domani','span':[0,6],'role':'time'}
  v,e=validate_x2({'note_id':'N1','actions':[self.action('devo pagare il bollo',[c])]},self.note)
  self.assertEqual(e,[]);self.assertEqual(v[0]['context'][0]['role'],'time')
 def test_bad_span(self):
  a=self.action('devo pagare il bollo');a['action_span']=[0,3]
  v,e=validate_x2({'note_id':'N1','actions':[a]},self.note)
  self.assertEqual(v,[]);self.assertTrue(any('ACTION_SPAN' in x for x in e))
 def test_no_auto_repair(self):
  a=self.action('devo pagare il bollo');a['action_quote']='pagare il bollo'
  v,e=validate_x2({'note_id':'N1','actions':[a]},self.note)
  self.assertEqual(v,[])
 def test_bad_context_rejects_action(self):
  a=self.action('devo pagare il bollo',[{'quote':'ieri','span':[0,4],'role':'time'}])
  v,e=validate_x2({'note_id':'N1','actions':[a]},self.note)
  self.assertEqual(v,[])
 def test_bad_target(self):
  a=self.action('devo pagare il bollo',relations=[{'target_id':'a99','type':'before'}])
  v,e=validate_x2({'note_id':'N1','actions':[a]},self.note)
  self.assertEqual(v,[])
 def test_note_id(self):
  a=self.action('devo pagare il bollo')
  self.assertEqual(validate_x2({'note_id':'other','actions':[a]},self.note)[0],[])
 def test_freeze(self):self.assertTrue(integrity())
 def test_dataset(self):self.assertEqual(len(read_cases(Path(__file__).parent/'note_test40_DIAGNOSTICO.json')),40)
 def test_schema_has_atomic_actions(self):self.assertIn('actions',REQUEST_SCHEMA['properties'])
 def test_no_quote_fabrication(self):
  a=self.action('devo pagare il bollo',[{'quote':'Domani','span':[0,6],'role':'time'}])
  v,_=validate_x2({'note_id':'N1','actions':[a]},self.note)
  self.assertEqual(project_quotes(v)['quotes'],['devo pagare il bollo'])

# Additional transport check: the structured response format must be sent only for X2.
class TestTransport(unittest.TestCase):
 def test_request_x2_transport_and_projection(self):
  from unittest.mock import patch
  from types import SimpleNamespace
  from prova_x0_x1_x2 import request_x2,X2
  note='Domani devo pagare il bollo.'
  q='devo pagare il bollo';start=note.index(q)
  answer={'note_id':'N1','actions':[{'id':'a1','action_quote':q,'action_span':[start,start+len(q)],'context':[{'quote':'Domani','span':[0,6],'role':'time'}],'relations':[]}]}
  params=SimpleNamespace(model='fake',url='http://localhost',timeout=10,max_tokens=350)
  trace={}
  with patch('prova_x0_x1_x2.call_server',return_value=(json.dumps(answer),'stop',{})) as mocked:
   result=request_x2(params,X2,'NOTA (DATI):\n'+json.dumps({'text':note}),{'nota':note},trace)
  self.assertEqual(result['json'],{'quotes':[q]})
  self.assertEqual(trace['accepted'][0]['context'][0]['quote'],'Domani')
  req=mocked.call_args.args[1]
  self.assertEqual(req['messages'][0]['content'],X2)
  self.assertEqual(req['response_format']['json_schema']['name'],'x2_atomic_actions')
  self.assertEqual(req['temperature'],0)
  self.assertEqual(req['seed'],42)

if __name__=="__main__":unittest.main(verbosity=2)
