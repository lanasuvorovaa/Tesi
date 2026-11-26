import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'pipeline_demo/frozen/selector'))
from selettore_s2 import choose_variant,veto_reasons,ranking_delta

def rec(q,cid='C1',z='PROPOSE',kind='TASK',note=None):
 return {'review_id':'TEST__'+cid,'scenario_id':'TEST','candidate_id':cid,'note_originale':note or q,'citazione':q,'tipo_predetto':kind,'intenzione_predetta':'COMMITTED','decisione_sandbox':z,'popup_mostrato':'0'}
class TestS2(unittest.TestCase):
 def test_veto_descriptive(self):self.assertIn('S2_V_DESCRIPTIVE_CLAUSE',veto_reasons(rec('La società attende i documenti')))
 def test_veto_aspiration(self):self.assertIn('S2_V_ASPIRATION_NO_ACTION',veto_reasons(rec('Forse un giorno aprirò un negozio')))
 def test_action_not_vetoed(self):self.assertEqual([],veto_reasons(rec('gli mando la scansione domattina')))
 def test_explicit_task_not_vetoed(self):self.assertEqual([],veto_reasons(rec('devo inviare il modulo')))
 def test_event_not_vetoed(self):self.assertEqual([],veto_reasons(rec('La lezione è confermata',kind='EVENT')))
 def test_r_does_not_veto(self):
  ds,sel=choose_variant([rec('Forse un giorno aprirò un negozio')],'S2-R')
  self.assertTrue(ds[0]['eligible']);self.assertIsNotNone(sel)
 def test_v_does_not_change_score(self):
  entries=[rec('Il cliente aspetta i documenti',note='Il cliente aspetta i documenti: gli mando la scansione.'),rec('gli mando la scansione',cid='C2',note='Il cliente aspetta i documenti: gli mando la scansione.')]
  s1,_=choose_variant(entries,'S1');v,_=choose_variant(entries,'S2-V')
  self.assertEqual([d['score'] for d in s1],[d['score'] for d in v])
 def test_r_does_not_change_eligibility(self):
  entries=[rec('Il cliente aspetta i documenti',note='Il cliente aspetta i documenti: gli mando la scansione.'),rec('gli mando la scansione',cid='C2',note='Il cliente aspetta i documenti: gli mando la scansione.')]
  s1,_=choose_variant(entries,'S1');r,_=choose_variant(entries,'S2-R')
  self.assertEqual([d['eligible'] for d in s1],[d['eligible'] for d in r])
 def test_z_block_never_reenabled(self):
  for variant in ('S1','S2-V','S2-R','S2-VR'):
   ds,sel=choose_variant([rec('devo inviare il modulo',z='BLOCKED')],variant)
   self.assertFalse(ds[0]['eligible']);self.assertIsNone(sel)
 def test_s1_old_cases(self):
  for q in ('o Luca','devo ancora decidere'):
   for variant in ('S1','S2-V','S2-R','S2-VR'):
    _,sel=choose_variant([rec(q)],variant);self.assertIsNone(sel)
 def test_selector_single_popup(self):
  entries=[rec('devo inviare il modulo'),rec('devo controllare la bozza',cid='C2',note='devo inviare il modulo; devo controllare la bozza')]
  for variant in ('S1','S2-V','S2-R','S2-VR'):
   _,sel=choose_variant(entries,variant);self.assertIsNotNone(sel)
if __name__=='__main__':unittest.main()
