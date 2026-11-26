"""Test offline: nessun modello o server richiesto."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import verifica

class TestVerifica(unittest.TestCase):
    def test_development_24(self):
        cases=verifica.get_cases()
        self.assertEqual(24,len(cases))
        self.assertEqual(24,len({c['id'] for c in cases}))
        self.assertTrue(all(c['origine']=='development_24_frozen' for c in cases))

    def test_prompt_congelato_dopo_diagnostico(self):
        self.assertEqual(hashlib.sha256(verifica.X1.encode()).hexdigest(),
                         '089e37cb73e1c361dd3d4e6a58b91d4e58d0aa08376c1e36ef0090a018fff1ca')

    def test_new_model_only_changes_extraction(self):
        args=object();calls=[];trace=[]
        def original(_a,s,u):calls.append('original-'+('X' if s==verifica.EXTRACT_X else 'C'));return {'json':{'quotes':[]}}
        def candidate(_a,u):calls.append('X1');return {'json':{'quotes':[]}}
        with patch.object(verifica,'request_constrained',side_effect=original),patch.object(verifica,'x1_call',side_effect=candidate):
            verifica.routed_call('qwen3.5-2b',args,verifica.EXTRACT_X,'test',trace)
            verifica.routed_call('qwen3.5-2b',args,verifica.CONTRAST,'test',trace)
            verifica.routed_call('qwen3-1.7b',args,verifica.EXTRACT_X,'test',trace)
            verifica.routed_call('qwen3-1.7b',args,verifica.CONTRAST,'test',trace)
        self.assertEqual(calls,['X1','original-C','original-X','original-C'])
        self.assertEqual([t['fase'] for t in trace],['X1','C0','X0','C0'])

    def test_json_schema_request_same_params(self):
        class Args:
            model='model-test';url='http://127.0.0.1:8091/v1';max_tokens=350;timeout=4
        reqs=[]
        def fake(url,body,timeout):
            reqs.append(body)
            return '{"quotes":["Domani devo prenotare il furgone"]}', 'stop', {}
        with patch.object(verifica,'call_server',side_effect=fake):
            result=verifica.x1_call(Args(),'NOTA (DATI): test')
        self.assertEqual(result['json']['quotes'],['Domani devo prenotare il furgone'])
        self.assertIsNone(result['error'])
        req=reqs[0]
        self.assertEqual((req['temperature'],req['seed'],req['max_tokens']),(0,42,350))
        self.assertEqual(req['messages'][0]['content'],verifica.X1)
        self.assertEqual(req['response_format']['type'],'json_schema')

    def test_test_cases_do_not_include_gold(self):
        f=Path(verifica.ROOT/'casi'/'development24.json').read_text(encoding='utf-8')
        self.assertNotIn('gold_output',f)
        self.assertNotIn('gold_annotation',f)

if __name__=='__main__':unittest.main()
