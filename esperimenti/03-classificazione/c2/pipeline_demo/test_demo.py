import json
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
from demo_core import analyze_note, make_scenario, DemoInputError

NOW=datetime(2026,11,2,12,0,tzinfo=ZoneInfo('Europe/Rome'))

def canned(obj):
    return {'raw':json.dumps(obj,ensure_ascii=False), 'json':obj,'parse_error':None,
            'finish_reason':'stop','usage':{},'latency_ms':1.5,'error':None}

def fake_call(extract, classifications):
    queue=[canned({'quotes':extract})]+[canned(x) for x in classifications]
    def call(args,system,user):
        if not queue:raise AssertionError('unexpected model request')
        return queue.pop(0)
    return call

class TestDemo(unittest.TestCase):
    def run_note(self,note,quotes,labels):
        return analyze_note(note,model='test-local',now=NOW,
                            request_fn=fake_call(quotes,labels))
    def test_task_is_simulated_not_saved(self):
        note='Domani devo prenotare il furgone.'
        result=self.run_note(note,['Domani devo prenotare il furgone'],
                             [{'kind':'TASK','intent':'COMMITTED'}])
        self.assertEqual(result['decision'],'PROPOSE')
        self.assertEqual(result['selected']['kind'],'TASK')
        self.assertFalse(result['runtime_capabilities_available'])
        self.assertEqual(result['candidates'][0]['actual_gate'],'BLOCKED')
        self.assertEqual(result['writes_performed'],0)
    def test_negation_does_not_become_popup(self):
        note='Non devo più chiamare il fornitore; devo invece scrivergli una mail.'
        result=self.run_note(note,['Non devo più chiamare il fornitore','devo invece scrivergli una mail'],
           [{'kind':'TASK','intent':'COMMITTED'},{'kind':'TASK','intent':'COMMITTED'}])
        self.assertFalse(result['candidates'][0]['eligible'])
        self.assertEqual(result['selected']['evidence'],'devo invece scrivergli una mail')
    def test_abstract_desire_suppressed_by_selector(self):
        note='Mi piacerebbe imparare il portoghese prima o poi.'
        result=self.run_note(note,['Mi piacerebbe imparare il portoghese prima o poi'],
                             [{'kind':'TASK','intent':'TENTATIVE'}])
        self.assertEqual(result['decision'],'NO_POPUP')
    def test_ill_formed_extract_fails_closed(self):
        result=analyze_note('Domani devo prenotare il furgone.', model='test-local',now=NOW,
                            request_fn=fake_call(['testo inesistente'],[]))
        self.assertEqual(result['decision'],'NO_POPUP')
        self.assertTrue(result['errors'])
    def test_empty_note_rejected(self):
        with self.assertRaises(DemoInputError):make_scenario('  ',NOW)
    def test_long_note_rejected(self):
        with self.assertRaises(DemoInputError):make_scenario('X'*601,NOW)
    def test_no_gold_or_snapshot_save(self):
        result=self.run_note('Ho già inviato il modulo.',['Ho già inviato il modulo'],[{'kind':'TASK','intent':'COMPLETED'}])
        self.assertFalse(result['preliminary_gold_used'])
        self.assertEqual(result['writes_performed'],0)
        self.assertEqual(result['decision'],'NO_POPUP')

if __name__=='__main__':unittest.main()
