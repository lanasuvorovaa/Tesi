"""Test di integrita del confronto; non eseguono inferenza."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile
import confronta
ROOT=Path(__file__).resolve().parent

class TestConfronto(unittest.TestCase):
    def test_casi_e_development(self):
        f1=json.loads((ROOT/'casi/fase1.json').read_text())['casi']
        f2=json.loads((ROOT/'casi/fase2.json').read_text())['casi']
        self.assertEqual(len(f1),10)
        self.assertEqual(len(f2),24)
        self.assertEqual(len({x['id'] for x in f2}),24)
        self.assertTrue(all(x['origine']=='development_24_frozen' for x in f2))
        self.assertTrue(all(x['nota'] and x['reference_datetime'] for x in f1+f2))
    def test_model_names_are_distinct(self):
        self.assertEqual(len(confronta.MODELS),3)
        self.assertTrue(all(x['min_bytes']>0 for x in confronta.MODELS.values()))
    def test_riga_json_e_popup(self):
        case={'id':'T1','nota':'Domani chiamo Marco','gruppo':'test'}
        res={'quotes':['Domani chiamo Marco'],'candidates':[{'kind':'TASK','intent':'COMMITTED',
               'evidence':'Domani chiamo Marco','sandbox_gate':'PROPOSE','eligible':True}],
             'selected':{'kind':'TASK','intent':'COMMITTED','evidence':'Domani chiamo Marco'},
             'decision':'PROPOSE','latency_ms':1000,'model_calls':2,'errors':[]}
        row=confronta.make_row(case,'qwen3-1.7b',res)
        self.assertEqual(row['tempo_s'],1.0)
        self.assertEqual(row['popup'],'SI')
        self.assertEqual(row['z_ammessi'],1)
    def test_json_is_written_only_in_report_path(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.json'
            confronta.write_json(p,{'test':'ok'})
            self.assertEqual(confronta.read_json(p)['test'],'ok')

if __name__=='__main__':unittest.main()
