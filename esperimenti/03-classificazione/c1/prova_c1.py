#!/usr/bin/env python3
"""UC-01 development experiment: X0 shared, C0 versus experimental C1, frozen Z/S.

Only the classification prompt changes. One real extraction per note is reused verbatim
for both classification variants. All user data remain in memory except local reports.
No calendar/task/note writes or external network calls.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "pipeline_demo"
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "frozen" / "xc_z"))
sys.path.insert(0, str(PIPELINE / "frozen" / "selector"))

from demo_core import analyze_note
from constrained_api import build_request, request_constrained
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST
from run_notes import call_server
from semantic_core_v6 import parse_json
from runtime_support import (PORT, URL, find_model, get_json, launch_server,
                             wait_server, stop_server)

C1 = (ROOT / "prompt_C1.txt").read_text(encoding="utf-8").strip()
KEYS = ("C0", "C1")
FRAG_FIELDS = ["caso", "frammento_id", "nota", "frammento", "c0_kind", "c0_intent",
               "c1_kind", "c1_intent", "c0_z", "c1_z", "c0_scelto", "c1_scelto",
               "c0_error", "c1_error", "tipo_atteso", "intenzione_attesa",
               "c0_corretta_SI_NO", "c1_corretta_SI_NO", "commento"]
NOTE_FIELDS = ["caso", "nota", "n_frammenti", "c0_etichette", "c1_etichette",
               "c0_popup", "c1_popup", "c0_testo", "c1_testo", "c0_tempo_s",
               "c1_tempo_s", "c0_errori", "c1_errori", "esito_manuale", "note_revisione"]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(2**20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def cases() -> list[dict]:
    data = json.loads((ROOT / "development24.json").read_text(encoding="utf-8"))
    records = data.get("casi", [])
    if len(records) != 24 or len({x.get("id") for x in records}) != 24:
        raise RuntimeError("Devono esserci esattamente 24 note development distinte")
    for entry in records:
        if entry.get("origine") != "development_24_frozen":
            raise RuntimeError("Trovato un caso che non appartiene al development congelato")
        if not entry.get("reference_datetime") or not entry.get("nota"):
            raise RuntimeError("Nota o data di riferimento mancante")
    return records


def request_c1(args, user):
    """Same constrained request as C0, but changes only system-prompt contents."""
    body = build_request(args.model, CONTRAST, user, args.max_tokens)
    body["messages"][0]["content"] = C1
    start = time.perf_counter()
    try:
        raw, finish, usage = call_server(args.url, body, args.timeout)
        parsed, parse_error = parse_json(raw)
        return {"raw": raw, "json": parsed, "parse_error": parse_error,
                "finish_reason": finish, "usage": usage,
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "error": None}
    except Exception as exc:
        return {"raw": None, "json": None, "parse_error": None,
                "finish_reason": None, "usage": {},
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "error": f"{type(exc).__name__}: {exc}"}


def run_pair(note: str, ref: datetime, model: str, url=URL,
             send_c0=request_constrained, send_c1=None):
    """Execute both variants with exactly one shared X0 extraction.

    Dependency hooks are solely for testing. In real use both send functions
    invoke the same local model endpoint.
    """
    if send_c1 is None:
        send_c1 = request_c1
    shared_x = {}
    traces = {"C0": [], "C1": []}

    def callback(variant, args, system, user):
        if system == EXTRACT_X:
            if variant == "C0":
                if shared_x:
                    raise RuntimeError("Estrazione X chiamata più di una volta per C0")
                response = send_c0(args, system, user)
                shared_x["response"] = copy.deepcopy(response)
            else:
                if "response" not in shared_x:
                    raise RuntimeError("C1 richiede l'estrazione già eseguita per C0")
                response = copy.deepcopy(shared_x["response"])
            stage = "X0_CONDIVISA"
            prompt = EXTRACT_X
        elif system == CONTRAST:
            response = send_c0(args, CONTRAST, user) if variant == "C0" else send_c1(args, user)
            stage = variant
            prompt = CONTRAST if variant == "C0" else C1
        else:
            raise RuntimeError("Prompt inatteso: non modificare altri componenti")
        traces[variant].append({"fase": stage,
                                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                                "richiesta": user,
                                "json": response.get("json"), "raw": response.get("raw"),
                                "error": response.get("error"),
                                "parse_error": response.get("parse_error"),
                                "latency_ms": response.get("latency_ms")})
        return response

    results = {}
    for variant in KEYS:
        results[variant] = analyze_note(note, model=model, url=url, timeout=240,
                                       now=ref,
                                       request_fn=lambda a, s, u, v=variant: callback(v, a, s, u))
    if results["C0"]["quotes"] != results["C1"]["quotes"]:
        raise AssertionError("Frammenti estratti diversi: esperimento non valido")
    if results["C0"]["extraction"] != results["C1"]["extraction"]:
        raise AssertionError("Estrazioni X0 non identiche")
    return results, traces


def by_evidence(result):
    """The frozen pipeline generates one candidate per valid classified quote."""
    return {c["evidence"]: c for c in result.get("candidates", [])}


def classified_label(trace, quote):
    # Classification requests use the original note and exact quote in a JSON dictionary.
    for item in trace:
        if item["fase"] not in KEYS:
            continue
        try:
            fragment = json.loads(item["richiesta"].split("\n", 1)[1])["fragment"]
        except (IndexError, ValueError, KeyError, TypeError):
            continue
        if fragment == quote:
            obj = item.get("json")
            if isinstance(obj, dict):
                return obj.get("kind", ""), obj.get("intent", ""), item.get("error") or item.get("parse_error") or ""
            return "", "", item.get("error") or item.get("parse_error") or "invalid classification"
    return "", "", "missing classification"


def make_rows(case, results, traces):
    note_row = {"caso": case["id"], "nota": case["nota"],
                "n_frammenti": len(results["C0"]["quotes"])}
    by_variant = {v: by_evidence(results[v]) for v in KEYS}
    for variant in KEYS:
        res = results[variant]
        selected = res.get("selected") or {}
        note_row[variant.lower() + "_etichette"] = " | ".join(
            f"{label[0] or '?'} / {label[1] or '?'}: {fragment}"
            for fragment in res["quotes"]
            for label in [classified_label(traces[variant], fragment)])
        note_row[variant.lower() + "_popup"] = "SI" if selected else "NO"
        note_row[variant.lower() + "_testo"] = selected.get("evidence", "")
        note_row[variant.lower() + "_tempo_s"] = round(res["latency_ms"] / 1000, 2)
        note_row[variant.lower() + "_errori"] = " | ".join(res["errors"])
    note_row["esito_manuale"] = ""
    note_row["note_revisione"] = ""
    fragments = []
    for i, quote in enumerate(results["C0"]["quotes"], 1):
        a = by_variant["C0"].get(quote, {})
        b = by_variant["C1"].get(quote, {})
        k0, it0, e0 = classified_label(traces["C0"], quote)
        k1, it1, e1 = classified_label(traces["C1"], quote)
        fragments.append({"caso": case["id"], "frammento_id": i,
                          "nota": case["nota"], "frammento": quote,
                          "c0_kind": k0, "c0_intent": it0,
                          "c1_kind": k1, "c1_intent": it1,
                          "c0_z": a.get("sandbox_gate", ""),
                          "c1_z": b.get("sandbox_gate", ""),
                          "c0_scelto": "SI" if a.get("selected") else "NO",
                          "c1_scelto": "SI" if b.get("selected") else "NO",
                          "c0_error": e0, "c1_error": e1,
                          "tipo_atteso": "", "intenzione_attesa": "",
                          "c0_corretta_SI_NO": "", "c1_corretta_SI_NO": "",
                          "commento": ""})
    return note_row, fragments


def render_report(note_rows, fragment_rows, manifest):
    lines = ["# Diagnostico UC-01 — classificazione C0 e C1 su Qwen3-1.7B", "",
             "**Fase:** development (24 note già conosciute). NON è validation indipendente.",
             "**Una sola modifica:** il prompt della classificazione C; X0, schema, Z, S, modello e parametri sono invariati.",
             "**Estrazione X0 condivisa:** ogni nota è estratta una volta, poi gli stessi frammenti sono classificati da C0 e C1.",
             "", "## Riepilogo operativo (non accuratezza)", "",
             "| Configurazione | Note | Popup | Segnalazioni | Tempo medio logico (s) |",
             "|---|---:|---:|---:|---:|"]
    for variant in KEYS:
        key = variant.lower()
        all_times = [r[key + "_tempo_s"] for r in note_rows if isinstance(r.get(key + "_tempo_s"), float)]
        avg = f"{sum(all_times)/len(all_times):.2f}" if all_times else "—"
        lines.append(f"| {variant} | {len(note_rows)} | {sum(r.get(key+'_popup')=='SI' for r in note_rows)} | "
                     f"{sum(bool(r.get(key+'_errori')) for r in note_rows)} | {avg} |")
    changes = [r for r in fragment_rows if (r["c0_kind"], r["c0_intent"]) != (r["c1_kind"], r["c1_intent"])]
    lines += ["", f"**Frammenti confrontabili:** {len(fragment_rows)}; **etichette modificate da C1:** {len(changes)}.",
              "Questi conteggi NON dimostrano che C1 sia migliore; verificare manualmente le etichette e il popup.",
              "", "## Dettaglio per nota", ""]
    for row in note_rows:
        lines.extend(["### " + row["caso"], "", "> " + row["nota"], "",
                      f"- **C0:** {row.get('c0_etichette') or '—'}; popup: {row.get('c0_popup') or '—'} «{row.get('c0_testo','')}»; errori: {row.get('c0_errori') or 'nessuno'}",
                      f"- **C1:** {row.get('c1_etichette') or '—'}; popup: {row.get('c1_popup') or '—'} «{row.get('c1_testo','')}»; errori: {row.get('c1_errori') or 'nessuno'}", ""])
    lines += ["## Come interpretare il confronto", "",
              "- Se X0 non estrae un'azione, C1 non può recuperarla. Segnalare separatamente il limite di estrazione.",
              "- TASK ed EVENT vanno valutati insieme all'intenzione; più popup non significano più correttezza.",
              "- Controllare con particolare attenzione azioni negate, già completate, contenuto citato e impegni tentativi.",
              "- UC01-MAIN-052 richiede chiarimento per la data vaga; un popup PROPOSE non è automaticamente appropriato.",
              "- Una classificazione corretta può comunque lasciare il suggerimento incompleto o senza data normalizzata.",
              "- Compilare `revisione_frammenti.csv` e `revisione_note.csv` prima di decidere se integrare C1.",
              "", "## Riproducibilità", "",
              f"- Qwen3-1.7B Q4; endpoint 127.0.0.1:{PORT}; CPU-only; `temperature=0`, `seed=42`, `max_tokens=350`, contesto=4096.",
              "- Stesso JSON schema di classificazione e stessa richiesta HTTP; cambia soltanto il testo system della classificazione.",
              f"- Hash prompt C0: `{manifest['prompt_C0_sha256']}`.",
              f"- Hash prompt C1: `{manifest['prompt_C1_sha256']}`.",
              "- I tempi sono tempi logici ricostruiti da X0 condivisa + classificazioni della rispettiva variante, non il tempo totale della doppia prova.",
              "- Nessuna modifica a dati personali, calendario o task; soltanto file diagnostici in una cartella locale."]
    return "\n".join(lines) + "\n"


def run(base: Path):
    data = cases()
    binary = base / "runtime" / "llama.cpp" / "build" / "bin" / "llama-server"
    if not binary.is_file():
        raise FileNotFoundError("Runtime aggiornato non trovato: " + str(binary))
    model_path = find_model("qwen3-1.7b")
    try:
        get_json("http://127.0.0.1:" + str(PORT) + "/health")
    except Exception:
        pass
    else:
        raise RuntimeError("Porta 8091 occupata. Chiudi il programma precedente prima di riprovare.")
    out = ROOT / "risultati" / ("c0_vs_c1_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    out.mkdir(parents=True, exist_ok=False)
    (out / "dettagli").mkdir()
    frozen_paths = [p for p in (PIPELINE / "frozen").rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".json"}]
    frozen_paths.sort()
    manifest = {"esperimento": "Qwen3-1.7B X0 + C0/C1 + Z + S",
                "casi": [c["id"] for c in data],
                "estrazione_condivisa": True,
                "nota": "Soltanto C cambia. Report di sviluppo; non accuratezza indipendente.",
                "modello": {"path": str(model_path), "size_bytes": model_path.stat().st_size,
                            "sha256": sha(model_path)},
                "runtime": {"path": str(binary), "sha256": sha(binary)},
                "prompt_X0_sha256": hashlib.sha256(EXTRACT_X.encode()).hexdigest(),
                "prompt_C0_sha256": hashlib.sha256(CONTRAST.encode()).hexdigest(),
                "prompt_C1_sha256": hashlib.sha256(C1.encode()).hexdigest(),
                "frozen_files_sha256": {str(p.relative_to(PIPELINE)): sha(p) for p in frozen_paths},
                "demo_core_sha256": sha(PIPELINE / "demo_core.py"),
                "dataset_sha256": sha(ROOT / "development24.json"),
                "parametri": {"temperature": 0, "seed": 42, "max_tokens": 350,
                              "context": 4096, "ngl": 0, "threads": 6},
                "scritture_utente": 0}
    save_json(out / "manifest.json", manifest)
    note_rows, frag_rows = [], []
    proc, fh = launch_server(binary, model_path, out / "llama_server.log")
    try:
        model_id = wait_server(proc)
        for index, case in enumerate(data, 1):
            print(f"[{index:02d}/24] {case['id']} — ", end="", flush=True)
            try:
                results, traces = run_pair(case["nota"], datetime.fromisoformat(case["reference_datetime"]), model_id)
                note_row, fragment_rows = make_rows(case, results, traces)
                note_rows.append(note_row)
                frag_rows.extend(fragment_rows)
                save_json(out / "dettagli" / (case["id"] + ".json"),
                          {"caso": case, "risultati": results, "tracce": traces})
                print(f"{note_row['n_frammenti']} frammenti; C0 popup {note_row['c0_popup']}; "
                      f"C1 popup {note_row['c1_popup']}", flush=True)
            except Exception as exc:
                fail = {"caso": case["id"], "nota": case["nota"],
                        "c0_errori": f"{type(exc).__name__}: {exc}",
                        "c1_errori": f"{type(exc).__name__}: {exc}"}
                note_rows.append(fail)
                save_json(out / "dettagli" / (case["id"] + "_errore.json"),
                          {"caso": case, "errore": traceback.format_exc()})
                print("ERRORE: " + str(exc), flush=True)
            save_csv(out / "confronto_note.csv", note_rows, NOTE_FIELDS)
            save_csv(out / "revisione_note.csv", note_rows, NOTE_FIELDS)
            save_csv(out / "confronto_frammenti.csv", frag_rows, FRAG_FIELDS)
            save_csv(out / "revisione_frammenti.csv", frag_rows, FRAG_FIELDS)
            (out / "report.md").write_text(render_report(note_rows, frag_rows, manifest), encoding="utf-8")
    finally:
        stop_server(proc, fh)
    print("\nRisultati salvati in: " + str(out))
    print("Apri report.md, confronto_frammenti.csv e confronto_note.csv.")
    print("Prima di scegliere C1, controlla manualmente i casi ambigui.")
    return out


def main():
    parser = argparse.ArgumentParser(description="Confronto sperimentale della sola classificazione C")
    parser.add_argument("--base", type=Path,
                        default=Path.home() / "Desktop" / "confronto_slm_uc01_v01")
    args = parser.parse_args()
    try:
        run(args.base.expanduser())
    except Exception as exc:
        print("ERRORE: " + type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
