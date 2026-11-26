import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'pipeline_demo/frozen/selector'))
from selettore_s1 import autonomy_reasons,choose_s1

def rec(q,kind='TASK',intent='COMMITTED',z='PROPOSE'):
 return {'review_id':'1','scenario_id':'N','candidate_id':'C','note_originale':q,
 'citazione':q,'tipo_predetto':kind,'intenzione_predetta':intent,
 'decisione_sandbox':z,'popup_mostrato':'0'}
class Tests(unittest.TestCase):
 def test_dangling_alternative(self):self.assertIn('S1_DANGLING_CONNECTOR',autonomy_reasons(rec('o Luca')))
 def test_other_alternative(self):self.assertIn('S1_DANGLING_CONNECTOR',autonomy_reasons(rec('oppure Paola')))
 def test_meta_decision(self):self.assertIn('S1_META_DECISION',autonomy_reasons(rec('devo ancora decidere')))
 def test_keep_email(self):self.assertEqual([],autonomy_reasons(rec('devo invece scrivergli una mail')))
 def test_keep_form(self):self.assertEqual([],autonomy_reasons(rec('Entro venerdì devo inviare il modulo di iscrizione')))
 def test_keep_quote_task(self):self.assertEqual([],autonomy_reasons(rec('domani devo controllarlo')))
 def test_keep_move(self):self.assertEqual([],autonomy_reasons(rec('imballare i libri')))
 def test_s1_not_modify_z(self):
  d,s=choose_s1([rec('devo ancora decidere')]);self.assertIsNone(s)
if __name__=='__main__':unittest.main()
