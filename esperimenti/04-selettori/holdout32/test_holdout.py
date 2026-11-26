import unittest,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'pipeline_demo/frozen/selector'))
from prova_holdout import check_frozen
from selettore_s1 import autonomy_reasons
from prova_s1_replay import select_s1
class TestHoldout(unittest.TestCase):
 def test_freeze(self):self.assertEqual(len(check_frozen()[1]),32)
 def test_autonomia(self):
  self.assertTrue(autonomy_reasons({'citazione':'oppure Andrea'}))
  self.assertFalse(autonomy_reasons({'citazione':'devo inviare il documento'}))
 def test_selettore_replay(self):
  c={'id':'C001','evidence':'devo ancora decidere','kind':'TASK','intent':'COMMITTED','sandbox_gate':'PROPOSE','selected':True}
  d,s=select_s1({'id':'T','nota':'devo ancora decidere'},{'candidates':[c]})
  self.assertIsNone(s)
if __name__=='__main__':unittest.main()
