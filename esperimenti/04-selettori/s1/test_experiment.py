"""Tests of the controlled comparison; no model or external server is needed."""
import hashlib
import json
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import prova_c2 as trial
from constrained_api import build_request, CLASSIFICATION_SCHEMA
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST

NOW = datetime(2026, 10, 12, 10, 0, tzinfo=ZoneInfo("Europe/Rome"))


def reply(obj):
    return {"raw": json.dumps(obj, ensure_ascii=False), "json": obj,
            "parse_error": None, "finish_reason": "stop", "usage": {},
            "latency_ms": 12.0, "error": None}


class ExperimentTest(unittest.TestCase):
    def test_data_is_frozen_development_only(self):
        records = trial.cases()
        self.assertEqual(len(records), 24)
        self.assertTrue(all(r["origine"] == "development_24_frozen" for r in records))

    def test_only_classification_prompt_is_new(self):
        self.assertIn("COMPLETED", trial.C2)
        self.assertIn("NEGATED", trial.C2)
        self.assertIn("EVENT", trial.C2)
        self.assertIn("TASK", trial.C2)
        self.assertIn("FACT", trial.C2)
        self.assertNotEqual(trial.C2, CONTRAST)
        self.assertIn("segmenti ATOMICI", EXTRACT_X)

    def test_json_schema_same_for_both_classifiers(self):
        c0 = build_request("qwen-test", CONTRAST, "contenuto", 350)
        self.assertEqual(c0["response_format"]["json_schema"]["schema"], CLASSIFICATION_SCHEMA)
        self.assertEqual(c0["temperature"], 0)
        self.assertEqual(c0["seed"], 42)
        self.assertFalse(c0["chat_template_kwargs"]["enable_thinking"])

    def test_c2_request_changes_only_prompt(self):
        from unittest.mock import patch
        with patch.object(trial, "call_server", return_value=('''{"kind":"TASK","intent":"COMMITTED"}''', "stop", {})) as mock:
            result = trial.request_c2(type("Args", (), {"model": "qwen-test", "url": "http://127.0.0.1:8091/v1", "timeout": 10, "max_tokens": 350})(), "contenuto")
        c0 = build_request("qwen-test", CONTRAST, "contenuto", 350)
        received = mock.call_args.args[1]
        self.assertEqual(received["messages"][0]["content"], trial.C2)
        c0["messages"][0]["content"] = trial.C2
        self.assertEqual(received, c0)
        self.assertEqual(result["json"]["kind"], "TASK")

    def test_shared_x0_and_frozen_z_s(self):
        note = 'Ieri ho restituito le chiavi. Domani devo prenotare il furgone.'
        fragments = ["Ieri ho restituito le chiavi", "Domani devo prenotare il furgone"]
        calls = {"X": 0, "C0": 0, "C2": 0}

        def c0(args, sys_prompt, user):
            if sys_prompt == EXTRACT_X:
                calls["X"] += 1
                return reply({"quotes": fragments})
            self.assertEqual(sys_prompt, CONTRAST)
            calls["C0"] += 1
            frag = json.loads(user.split("\n", 1)[1])["fragment"]
            return reply({"kind": "TASK", "intent": "COMPLETED" if frag == fragments[0] else "COMMITTED"})

        def c2(args, user):
            calls["C2"] += 1
            frag = json.loads(user.split("\n", 1)[1])["fragment"]
            return reply({"kind": "TASK", "intent": "COMPLETED" if frag == fragments[0] else "COMMITTED"})

        results, traces = trial.run_pair(note, NOW, "test-model", send_c0=c0, send_c2=c2)
        self.assertEqual(calls, {"X": 1, "C0": 2, "C2": 2})
        self.assertEqual(results["C0"]["quotes"], results["C2"]["quotes"])
        self.assertEqual(traces["C0"][0]["json"], traces["C2"][0]["json"])
        self.assertEqual(results["C2"]["writes_performed"], 0)
        self.assertEqual(results["C0"]["writes_performed"], 0)
        self.assertEqual(results["C2"]["selected"]["evidence"], fragments[1])
        self.assertEqual(results["C0"]["selected"]["evidence"], fragments[1])
        row, fragments_rows = trial.make_rows({"id": "TEST", "nota": note}, results, traces)
        self.assertEqual(len(fragments_rows), 2)
        self.assertEqual(fragments_rows[0]["c0_intent"], "COMPLETED")
        self.assertEqual(fragments_rows[1]["c2_intent"], "COMMITTED")
        self.assertEqual(row["c2_popup"], "SI")

    def test_rejected_negation_remains_rejected(self):
        note = 'Non devo più chiamare il fornitore; devo invece scrivergli una mail.'
        fragments = ['Non devo più chiamare il fornitore', 'devo invece scrivergli una mail']

        def c0(a, prompt, user):
            if prompt == EXTRACT_X:
                return reply({'quotes': fragments})
            quote = json.loads(user.split('\n', 1)[1])['fragment']
            return reply({'kind':'TASK', 'intent':'NEGATED' if quote == fragments[0] else 'COMMITTED'})

        def c2(a, user):
            quote = json.loads(user.split('\n', 1)[1])['fragment']
            return reply({'kind':'TASK', 'intent':'NEGATED' if quote == fragments[0] else 'COMMITTED'})

        results, _ = trial.run_pair(note, NOW, 'test-model', send_c0=c0, send_c2=c2)
        for variant in ('C0', 'C2'):
            self.assertEqual(results[variant]['selected']['evidence'], fragments[1])
            self.assertEqual(results[variant]['candidates'][0]['sandbox_gate'], 'BLOCKED')


if __name__ == '__main__':
    unittest.main()
