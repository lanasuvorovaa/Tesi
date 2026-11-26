"""Controlli offline senza inferenza, senza GUI e senza dati utente."""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from pipeline.demo_core import analyze_note

class TestIntegrazione(unittest.TestCase):
    def test_pipeline_seleziona_task_senza_scrivere(self):
        calls=[]
        def fake(args,system,user):
            calls.append(user)
            value={'quotes':['Domani devo prenotare il furgone.']} if len(calls)==1 else {'kind':'TASK','intent':'COMMITTED'}
            return {'json':value,'raw':'{}','parse_error':None,'error':None,'latency_ms':1,'finish_reason':'stop','usage':{}}
        result=analyze_note('Domani devo prenotare il furgone.',model='test',request_fn=fake,
                            now=datetime(2026,11,26,12,tzinfo=ZoneInfo('Europe/Rome')))
        self.assertEqual(len(calls),2)
        self.assertEqual(result['decision'],'PROPOSE')
        self.assertEqual(result['writes_performed'],0)
        self.assertTrue(result['sandbox_only'])
        self.assertFalse(result['confirmation_performed'])

if __name__=='__main__': unittest.main()
