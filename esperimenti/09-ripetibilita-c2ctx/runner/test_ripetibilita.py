import unittest,json
from pathlib import Path
from prova_ripetibilita import samples,h,summarize
ROOT=Path(__file__).parent
class RepeatTests(unittest.TestCase):
 def setUp(self):
  self.d0=json.loads((ROOT/'interfaccia_I1_ORIGINALE.json').read_text())
  self.d1=json.loads((ROOT/'interfaccia_I1_R_REVISIONATA.json').read_text())
 def test_focus_count(self):
  p,r=samples(self.d0,self.d1,'focus');self.assertEqual(len(p),20);self.assertEqual(len(r),18)
 def test_all_count(self):
  p,r=samples(self.d0,self.d1,'all');self.assertEqual(len(p),39)
 def test_input_sha_stable(self):self.assertEqual(h('identico'),h('identico'))
 def test_summary_detects_change(self):
  p,_=samples(self.d0,self.d1,'focus');n,a,_=p[0];key={'caso':n['note_id'],'azione_id':a['id']}
  rows=[dict(key,json_valido=1,kind='TASK',intent='COMMITTED',subject_owner='SELF',polarity='POSITIVE',completion='PENDING',uncertain=False),dict(key,json_valido=1,kind='EVENT',intent='COMMITTED',subject_owner='SELF',polarity='POSITIVE',completion='PENDING',uncertain=False)]
  # summarize only first action
  r=summarize(rows,[p[0]],2);self.assertEqual(r[0]['identico_tutte_le_volte'],0)
  self.assertEqual(r[0]['valori_distinti_kind'],2)
if __name__=='__main__':unittest.main()
