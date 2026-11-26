import unittest, tempfile, json
from pathlib import Path
from prova_c2_ctx import prepare,valid,SCHEMA,user_c2,user_ctx,freeze_check
ROOT=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_freeze(self):self.assertIn('model_sha256',freeze_check())
 def test_paired_documents(self):
  doc,flags=prepare(ROOT/'estrazioni_x2_congelate.json',ROOT/'note_test40_DIAGNOSTICO.json')
  self.assertEqual(len(doc['notes']),40)
  self.assertGreater(sum(len(n['actions']) for n in doc['notes']),0)
 def test_schemas(self):
  self.assertTrue(valid({'kind':'TASK','intent':'COMMITTED'},'C2'))
  self.assertFalse(valid({'kind':'TASK','intent':'COMMITTED','extra':1},'C2'))
  obj={k:(False if k=='uncertain' else v['enum'][0]) for k,v in SCHEMA['properties'].items()}
  self.assertTrue(valid(obj,'C2-CTX'))
  self.assertFalse(valid(dict(obj,uncertain='false'),'C2-CTX'))
 def test_inputs_distinct(self):
  doc,_=prepare(ROOT/'estrazioni_x2_congelate.json',ROOT/'note_test40_DIAGNOSTICO.json')
  x=next(n for n in doc['notes'] if n['actions']);a=x['actions'][0]
  self.assertEqual(json.loads(user_c2(x['text'],a).split('\n',1)[1])['fragment'],a['action_evidence']['quote'])
  self.assertEqual(json.loads(user_ctx(x['text'],a).split('\n',1)[1])['action_id'],a['id'])
if __name__=='__main__':unittest.main()
