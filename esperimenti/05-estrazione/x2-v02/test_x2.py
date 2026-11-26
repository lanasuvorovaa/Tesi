import unittest,json
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from x2_core import locate,align_x2,project_quotes,REQUEST_SCHEMA,strip_v01_spans
from prova_x0_x1 import integrity,read_cases
class AlignmentTests(unittest.TestCase):
 def setUp(self):self.note='Domani devo pagare il bollo e inviare la ricevuta alla contabilità.'
 def a(self,quote,aid='a1',context=None,relations=None):
  return {'id':aid,'action_quote':quote,'context':context or [],'relations':relations or []}
 def test_offsets(self):
  p=self.note.index('devo pagare il bollo');self.assertEqual(locate(self.note,'devo pagare il bollo'),([p,p+len('devo pagare il bollo')],None))
 def test_unicode_offsets(self):
  note='È ora di pagare l’abbonamento';quote='pagare l’abbonamento';p=note.index(quote)
  self.assertEqual(locate(note,quote),([p,p+len(quote)],None))
 def test_missing(self):self.assertEqual(locate(self.note,'inviare soldi')[1],'QUOTE_NOT_FOUND')
 def test_ambiguous(self):self.assertEqual(locate('chiamo Luca poi chiamo Luca','chiamo Luca')[1],'AMBIGUOUS_QUOTE')
 def test_two_actions(self):
  v,e=align_x2({'note_id':'N1','actions':[self.a('devo pagare il bollo'),self.a('inviare la ricevuta alla contabilità','a2')]},self.note)
  self.assertEqual(len(v),2);self.assertEqual(e,[])
 def test_context(self):
  v,e=align_x2({'note_id':'N1','actions':[self.a('devo pagare il bollo',context=[{'quote':'Domani','role':'time'}])]},self.note)
  self.assertEqual(e,[]);self.assertEqual(v[0]['context'][0]['span'],[0,6])
 def test_invalid_context_rejects_action(self):
  v,e=align_x2({'note_id':'N1','actions':[self.a('devo pagare il bollo',context=[{'quote':'ieri','role':'time'}])]},self.note)
  self.assertFalse(v);self.assertIn('action[0]:CONTEXT[0]_QUOTE_NOT_FOUND',e)
 def test_self_relation_rejected(self):
  v,e=align_x2({'note_id':'N1','actions':[self.a('devo pagare il bollo',relations=[{'target_id':'a1','type':'before'}])]},self.note)
  self.assertFalse(v);self.assertIn('action[0]:RELATION[0]_SELF_REFERENCE',e)
 def test_dangling_relation(self):
  v,e=align_x2({'note_id':'N1','actions':[self.a('devo pagare il bollo',relations=[{'target_id':'a2','type':'before'}])]},self.note)
  self.assertFalse(v)
 def test_no_hallucination(self):
  v,e=align_x2({'note_id':'N1','actions':[self.a('inviare soldi')]},self.note)
  self.assertFalse(v)
 def test_projection(self):
  v,_=align_x2({'note_id':'N1','actions':[self.a('devo pagare il bollo')]},self.note)
  self.assertEqual(project_quotes(v),{'quotes':['devo pagare il bollo']})
 def test_legacy_stripping(self):
  raw={'note_id':'N1','actions':[{'id':'a1','action_quote':'devo pagare il bollo','action_span':[4,5],'context':[{'quote':'Domani','span':[0,6],'role':'time'}],'relations':[]}]}
  a=strip_v01_spans(raw);self.assertNotIn('action_span',a['actions'][0]);self.assertNotIn('span',a['actions'][0]['context'][0])
 def test_schema(self):self.assertNotIn('action_span',REQUEST_SCHEMA['properties']['actions']['items']['properties'])
 def test_frozen(self):self.assertTrue(integrity())
 def test_cases(self):self.assertEqual(len(read_cases(Path(__file__).parent/'note_test40_DIAGNOSTICO.json')),40)
 def test_request_transport(self):
  from prova_x0_x1_x2 import request_x2,X2
  q='devo pagare il bollo';case={'nota':self.note};answer={'note_id':'N1','actions':[self.a(q)]}
  params=SimpleNamespace(model='fake',url='http://localhost',timeout=10,max_tokens=350)
  trace={}
  with patch('prova_x0_x1_x2.call_server',return_value=(json.dumps(answer),'stop',{})) as mock:
   result=request_x2(params,X2,'test',case,trace)
  self.assertEqual(result['json'],{'quotes':[q]});self.assertEqual(trace['accepted'][0]['action_span'],[self.note.index(q),self.note.index(q)+len(q)])
  self.assertEqual(mock.call_args.args[1]['response_format']['json_schema']['schema'],REQUEST_SCHEMA)
if __name__=='__main__':unittest.main(verbosity=2)
