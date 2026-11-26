import unittest,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from prova_i1r import verify_pair
from prova_c2_ctx import prepare,user_ctx,freeze_check
class TestI1R(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.orig=json.loads((ROOT/'interfaccia_I1_ORIGINALE.json').read_text())
  cls.rev=json.loads((ROOT/'interfaccia_I1_R_REVISIONATA.json').read_text())
 def test_structure(self):self.assertEqual(len(verify_pair(self.orig,self.rev)),18)
 def test_original_identical(self):
  prepared,_=prepare(ROOT/'estrazioni_x2_congelate.json',ROOT/'note_test40_DIAGNOSTICO.json')
  self.assertEqual(self.orig,prepared)
 def test_unchanged_28(self):
  self.assertEqual(sum(x['actions']==y['actions'] for x,y in zip(self.orig['notes'],self.rev['notes'])),28)
 def test_prompt_unchanged(self):
  self.assertIn('AZIONE E CONTESTO',user_ctx('test',{'id':'a1','action_evidence':{'quote':'x','span':[0,1]},'context_refs':[]}))
 def test_freeze(self):self.assertIn('sha256',freeze_check())
 def test_local_negation(self):
  n=next(n for n in self.rev['notes'] if n['note_id'].endswith('028'))
  self.assertEqual(len(n['actions']),1)
  self.assertTrue(all(r['scope']==['a1'] for r in n['actions'][0]['context_refs']))
if __name__=='__main__':unittest.main()
