"""Live UC-01 demonstrator. Frozen X/C/Z and frozen selector are imported unchanged.

IMPORTANT: Only sandbox decision simulation. Never write to user data. The model never
receives benchmark gold. The original note is held in memory for a single request.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "frozen" / "xc_z"))
sys.path.insert(0, str(BASE / "frozen" / "selector"))

from constrained_api import request_constrained
from experiment_controls import EXTRACT_X, replay_security
from run_pipeline_bc import CONTRAST, stage1_check, assemble
from run_notes import get_model
from replay_24 import choose

SCHEMA = json.loads((BASE / "frozen/xc_z/schemas/uc01-gold.schema.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((BASE / "frozen/xc_z/data/capability_registry.json").read_text(encoding="utf-8"))

class DemoInputError(ValueError):
    pass


def make_scenario(note: str, now: datetime | None = None):
    if not isinstance(note, str) or not note.strip():
        raise DemoInputError("Inserisci una nota da analizzare.")
    note = note.strip()
    if len(note) > 600:
        raise DemoInputError("Per la demo inserisci una nota di massimo 600 caratteri.")
    if now is None:
        now = datetime.now(ZoneInfo("Europe/Rome"))
    if now.tzinfo is None:
        raise DemoInputError("La data di riferimento deve avere un fuso orario.")
    s = {"schema_version": "benchmark-data.v1", "scenario_id": "DEMO-LIVE", "use_case": "UC01",
         "dataset_split": "demo_only", "reference_datetime": now.isoformat(),
         "timezone": "Europe/Rome", "input": {"operation": "ANALYZE_NOTE", "source_id": "N1", "text": note},
         "workspace": {"snapshot_id": "DEMO-LIVE-SNAPSHOT"}}
    snap = {"schema_version": "workspace-snapshot.v1", "snapshot_id": "DEMO-LIVE-SNAPSHOT",
            "nodes": [{"node_id":"N1", "kind":"NOTE", "title":"Nota demo", "revision":1,
                       "content":note, "aliases":[], "metadata":{}}],
            "relations":[], "evidence":[],
            "source_revisions":[{"source_item_id":"N1", "revision":1, "content":note}],
            "external_sources":[]}
    return s, snap


def available_model(url: str):
    data = get_model(url)
    ids = [entry.get("id") or entry.get("name") for entry in data.get("data", [])]
    if not ids:
        ids = [entry.get("id") or entry.get("name") for entry in data.get("models", [])]
    ids = [x for x in ids if isinstance(x, str) and x]
    if not ids:
        raise RuntimeError("Il server non restituisce un identificativo del modello.")
    if len(ids) > 1:
        raise RuntimeError("La demo richiede un solo modello: il server ne espone più di uno.")
    if not re.search(r"qwen.?3.*1[.,_-]?7b", ids[0].lower()):
        raise RuntimeError("Il server non espone Qwen3-1.7B: modello disponibile " + ids[0])
    return ids[0]


def analyze_note(note: str, url: str = "http://127.0.0.1:8080/v1", model: str | None = None,
                 max_tokens: int = 350, timeout: int = 120, request_fn=None, now=None):
    """Inference exactly from frozen X/C. Applies frozen Z then frozen selector.

    `request_fn` is injected only by unit tests; production defaults to frozen
    `request_constrained`. Gold and scores are never read by this module.
    """
    scenario, snapshot = make_scenario(note, now)
    if request_fn is None:
        request_fn = request_constrained
    if model is None:
        model = available_model(url)
    args = SimpleNamespace(model=model, url=url, max_tokens=max_tokens, timeout=timeout)
    original = scenario["input"]["text"]
    extraction = request_fn(args, EXTRACT_X, "NOTA (DATI):\n" + json.dumps({"text":original}, ensure_ascii=False))
    quotes, stage1_errors = stage1_check(extraction.get("json"), original)
    extraction["validation_errors"] = stage1_errors
    classified = [request_fn(args, CONTRAST, "CONTESTO E FRAMMENTO (dati):\n" +
                             json.dumps({"note":original,"fragment":q},ensure_ascii=False)) for q in quotes]
    rec = assemble(scenario, snapshot, REGISTRY, SCHEMA, args, quotes, extraction, classified, "C")
    rec["mode"] = "X_EXTRACT_ONLY"
    gated = replay_security(rec, scenario)
    prediction = gated.get("converted_output") or {}
    ev_map = {e["evidence_id"]:e.get("quote", "") for e in prediction.get("evidence", [])}
    gate_map = {g["candidate_id"]:g for g in gated["gates"]["sandbox"]["candidates"]}
    strict_map = {g["candidate_id"]:g for g in gated["gates"]["registry_strict"]["candidates"]}
    previous_popup = gated["gates"]["sandbox"]["single_popup_candidate_id"]
    rows = []
    for candidate in prediction.get("candidates", []):
        cid = candidate["candidate_id"]
        sources = [ev_map[eid] for eid in candidate["evidence_ids"] if eid in ev_map]
        # `frozen_selector` expects a single contiguous evidence quote.
        if len(sources) != 1:
            continue
        rows.append({"scenario_id": "DEMO-LIVE", "candidate_id":cid,
                     "review_id": "DEMO-LIVE__" + cid,
                     "note_originale":original, "citazione":sources[0],
                     "testo_candidato":candidate.get("canonical_text", sources[0]),
                     "tipo_predetto":candidate["kind"],
                     "intenzione_predetta":candidate["intent_status"],
                     "decisione_sandbox":gate_map[cid]["decision"],
                     "popup_mostrato": "1" if previous_popup == cid else "0"})
    diagnostics, selected = choose(rows)
    diag_by_id = {d["candidate_id"]: d for d in diagnostics}
    options = []
    for item in rows:
        cid = item["candidate_id"]
        d = diag_by_id[cid]
        options.append({"id":cid, "evidence":item["citazione"],
                        "kind":item["tipo_predetto"], "intent":item["intenzione_predetta"],
                        "sandbox_gate":gate_map[cid]["decision"],
                        "actual_gate":strict_map[cid]["decision"],
                        "sandbox_reasons":gate_map[cid].get("reasons", []),
                        "actual_reasons":strict_map[cid].get("reasons", []),
                        "eligible":d["eligible"],"selector_score":d["score"],
                        "selector_reasons":d["reject_reasons"],
                        "selected":bool(selected and selected["candidate_id"] == cid)})
    selected_option = next((o for o in options if o["selected"]), None)
    errors = []
    if extraction.get("error"): errors.append("ERRORE_ESTRAZIONE: " + extraction["error"])
    if extraction.get("parse_error"): errors.append("JSON_ESTRAZIONE_NON_VALIDO")
    errors.extend(stage1_errors)
    for r in classified:
        if r.get("error"): errors.append("ERRORE_CLASSIFICAZIONE: " + r["error"])
        if r.get("parse_error"): errors.append("JSON_CLASSIFICAZIONE_NON_VALIDO")
    errors.extend(rec.get("schema_errors", []))
    errors.extend(rec.get("evidence_errors", []))
    errors.extend(rec.get("conversion_errors", []))
    errors.extend([str(d.get("reason")) for d in rec.get("stage1_errors", [])])
    notices = []
    if re.search(r"\bprossimo fine settimana\b", original, re.I):
        notices.append("La politica di prodotto richiede una data precisa: il prompt congelato può non rispettare questa regola. Verificare l'esito, senza correggerlo artificialmente.")
    if re.search(r"\b(?:prima|dopo)\b", original, re.I):
        notices.append("Le relazioni di precedenza e la gestione degli orari non sono ancora implementate nella demo UC-01.")
    if len(quotes) != len(options):
        notices.append("Alcuni frammenti estratti non sono diventati candidati validi. Consultare i diagnostici.")
    if selected_option and selected_option["kind"] == "EVENT" and not any(c.get("temporal") for c in prediction.get("candidates", []) if c["candidate_id"] == selected_option["id"]):
        notices.append("La proposta non contiene una data normalizzata: il riferimento temporale resta nella nota originale.")
    return {
        "note": original, "model":model, "reference_datetime":scenario["reference_datetime"],
        "pipeline":"X + C + Z + selettore deterministico (copie congelate)",
        "schema_valid":bool(rec.get("schema_valid")),
        "quotes":quotes, "candidates":options,
        "selected":selected_option,
        "decision":selected_option["sandbox_gate"] if selected_option else "NO_POPUP",
        "errors":errors, "notices":notices,
        "latency_ms":round(gated.get("latency_ms",0),1),
        "model_calls":1+len(quotes),
        "writes_performed":0,"confirmation_performed":False,
        "sandbox_only":True,"runtime_capabilities_available":False,
        "frozen_files_changed":False,
        "preliminary_gold_used":False,
        "extraction": {"raw":extraction.get("raw"), "json":extraction.get("json"), "errors":stage1_errors},
        "diagnostics": {"schema_errors":rec.get("schema_errors", []),
                        "evidence_errors":rec.get("evidence_errors", []),
                        "conversion_errors":rec.get("conversion_errors", []),
                        "semantic_veto_audit":gated.get("semantic_veto_audit", []),
                        "strict_gate":gated["gates"]["registry_strict"],
                        "candidate_selector":diagnostics},
    }
