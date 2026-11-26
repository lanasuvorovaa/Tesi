import copy
import json
import unittest
from pathlib import Path
from valida_interfaccia import validate_document

BASE=json.loads((Path(__file__).parent/'esempio_028_031.json').read_text(encoding='utf-8'))

class Tests(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(validate_document(BASE),{'notes':2,'actions':4})
    def test_invented_quote_rejected(self):
        doc=copy.deepcopy(BASE)
        doc['notes'][0]['actions'][0]['action_evidence']['quote']='comprare biglietti'
        with self.assertRaises(ValueError):validate_document(doc)
    def test_bad_span_rejected(self):
        doc=copy.deepcopy(BASE)
        doc['notes'][0]['actions'][0]['action_evidence']['span']=[0,3]
        with self.assertRaises(ValueError):validate_document(doc)
    def test_scope_rejected(self):
        doc=copy.deepcopy(BASE)
        doc['notes'][0]['actions'][0]['context_refs'][0]['scope']=['missing']
        with self.assertRaises(ValueError):validate_document(doc)
    def test_relation_rejected(self):
        doc=copy.deepcopy(BASE)
        doc['notes'][0]['relations'][0]['target_action_id']='missing'
        with self.assertRaises(ValueError):validate_document(doc)

if __name__=='__main__':unittest.main()
