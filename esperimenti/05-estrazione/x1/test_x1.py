#!/usr/bin/env python3
import unittest, tempfile, json
from unittest.mock import patch
from types import SimpleNamespace
from pathlib import Path
from prova_x0_x1 import read_cases,extract_comparison,integrity,X1,EXTRACT_X,request_x1
from run_pipeline_bc import stage1_check

class ExperimentTests(unittest.TestCase):
 def test_x1_transport_preserves_schema_and_params(self):
  params=SimpleNamespace(model='test-model',max_tokens=350,url='http://localhost',timeout=12)
  with patch('prova_x0_x1.call_server',return_value=('{"quotes":["test"]}','stop',{})) as call:
   r=request_x1(params,X1,'test')
  self.assertEqual(r['json'],{'quotes':['test']})
  req=call.call_args.args[1]
  self.assertEqual(req['messages'][0]['content'],X1)
  self.assertEqual(req['messages'][1]['content'],'test')
  self.assertEqual(req['response_format']['json_schema']['name'],'atomic_quotes')
  self.assertEqual(req['temperature'],0)
  self.assertEqual(req['seed'],42)
 def test_frozen(self):
  self.assertTrue(integrity())
 def test_prompt_isolated(self):
  self.assertNotEqual(X1,EXTRACT_X)
 def test_input(self):
  self.assertEqual(len(read_cases(Path(__file__).parent/'note_test40_DIAGNOSTICO.json')),40)
 def test_tz_reject(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.json';p.write_text(json.dumps([{'id':'a','nota':'test','reference_datetime':'2026-12-03T10:00:00'}]))
   with self.assertRaises(ValueError):read_cases(p)
 def test_validator_kept(self):
  q,err=stage1_check({'quotes':['devo spedire un pacco','testo inventato']},'Oggi devo spedire un pacco.')
  self.assertTrue(err)
  self.assertEqual(q,['devo spedire un pacco'])
 def test_result_without_candidates(self):
  case={'id':'t','nota':'Una nota.'}
  result={'extraction':{'json':{'quotes':[]},'errors':[]},'quotes':[],'candidates':[],'errors':[]}
  row,cs=extract_comparison(case,'X0',result)
  self.assertEqual(row['popup'],'NO');self.assertEqual(cs,[])
if __name__=='__main__':unittest.main()
