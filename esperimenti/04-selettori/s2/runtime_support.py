#!/usr/bin/env python3
"""Confronto diagnostico offline UC-01 su modelli locali, senza modificare X/C/Z/S.

Ogni modello usa la stessa copia di demo_core.py, gli stessi prompt e i medesimi
parametri JSON. Il progetto esegue SOLO simulazioni, nessuna scrittura di task/eventi.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = {
    "qwen3-1.7b": {
        "paths": ["qwen3-1.7b-q4.gguf"], "min_bytes": 850_000_000,
        "provenienza": "modello gia presente sul Mac (Qwen3-1.7B Q4)"
    },
    "qwen3.5-2b": {
        "paths": ["qwen3.5-2b-q4_k_m.gguf", "Qwen_Qwen3.5-2B-Q4_K_M.gguf"],
        "min_bytes": 1_000_000_000,
        "provenienza": "bartowski/Qwen_Qwen3.5-2B-GGUF Q4_K_M"
    },
    "lfm2.5-1.2b": {
        "paths": ["lfm2.5-1.2b-instruct-q4_k_m.gguf", "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"],
        "min_bytes": 600_000_000,
        "provenienza": "LiquidAI/LFM2.5-1.2B-Instruct-GGUF Q4_K_M"
    },
}
PORT = 8091
URL = f"http://127.0.0.1:{PORT}/v1"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def check_gguf(path: Path, minimum: int):
    if not path.is_file() or path.stat().st_size < minimum:
        return False
    with path.open("rb") as fh:
        return fh.read(4) == b"GGUF"


def find_model(key):
    base = Path.home() / "models"
    for name in MODELS[key]["paths"]:
        p = base / name
        if check_gguf(p, MODELS[key]["min_bytes"]):
            return p
    raise FileNotFoundError(
        f"Modello {key} mancante/non completo in {base}. "
        "Esegui prima: bash 02_scarica_modelli.command"
    )


def server_bin():
    p = ROOT / "runtime" / "llama.cpp" / "build" / "bin" / "llama-server"
    if not p.is_file():
        raise FileNotFoundError("Runtime mancante: esegui prima bash 01_prepara_runtime.command")
    return p


def get_json(url):
    with urllib.request.urlopen(url, timeout=2) as resp:
        return json.load(resp)


def launch_server(binary: Path, model_path: Path, logfile: Path):
    env = os.environ.copy()
    env["DYLD_LIBRARY_PATH"] = str(binary.parent) + (
        ":" + env["DYLD_LIBRARY_PATH"] if env.get("DYLD_LIBRARY_PATH") else ""
    )
    fh = logfile.open("w", encoding="utf-8")
    cmd = [str(binary), "-m", str(model_path), "--host", "127.0.0.1", "--port", str(PORT),
           "-c", "4096", "-ngl", "0", "--threads", "6"]
    proc = subprocess.Popen(cmd, cwd=binary.parent, env=env, stdout=fh,
                            stderr=subprocess.STDOUT, start_new_session=True)
    return proc, fh


def wait_server(proc, seconds=120):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if proc.poll() is not None:
            raise RuntimeError(f"llama-server terminato all'avvio (codice {proc.returncode})")
        try:
            h = get_json(f"http://127.0.0.1:{PORT}/health")
            if h.get("status") == "ok":
                data = get_json(URL + "/models")
                ids = [x.get("id") for x in data.get("data", []) if x.get("id")]
                if len(ids) != 1:
                    raise RuntimeError("Il server deve esporre un solo modello, ne espone: " + repr(ids))
                return ids[0]
        except (OSError, ValueError, TimeoutError, urllib.error.URLError):
            pass
        time.sleep(2)
    raise TimeoutError("llama-server non pronto; consulta il log del modello")


def stop_server(proc, fh):
    try:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
    finally:
        fh.close()


def make_row(case, model_key, result, err=""):
    candidates = result.get("candidates", []) if result else []
    selected = (result.get("selected") or {}) if result else {}
    raw_quotes = result.get("quotes", []) if result else []
    errors = result.get("errors", []) if result else []
    return {
        "caso": case["id"], "gruppo": case["gruppo"], "modello": model_key,
        "stato": "ERRORE" if err else ("SEGNALAZIONI" if errors else "ESEGUITO"),
        "nota": case["nota"], "frammenti": len(raw_quotes),
        "frammenti_testo": " | ".join(map(str, raw_quotes)),
        "candidati": len(candidates),
        "etichette": " | ".join(f"{c['kind']}/{c['intent']}:{c['evidence']}" for c in candidates),
        "z_ammessi": sum(c.get("sandbox_gate") in {"PROPOSE", "CLARIFY"} for c in candidates),
        "selettore_ammessi": sum(bool(c.get("eligible")) for c in candidates),
        "popup": "SI" if selected else "NO",
        "popup_testo": selected.get("evidence", ""),
        "popup_tipo": selected.get("kind", ""),
        "popup_intent": selected.get("intent", ""),
        "decisione": result.get("decision", "") if result else "",
        "tempo_s": round(float(result.get("latency_ms", 0)) / 1000, 2) if result else "",
        "chiamate": result.get("model_calls", "") if result else "",
        "errori": " | ".join(map(str, errors)) if not err else err,
    }


FIELDS = list(make_row({"id":"x", "gruppo":"x", "nota":"x"}, "x", {}).keys())
REVIEW_FIELDS = ["caso", "gruppo", "modello", "nota", "frammenti_testo", "etichette",
                 "popup_testo", "evento_corretto_SI_NO_NA", "task_corretto_SI_NO_NA",
                 "intenzioni_corrette_SI_NO_NA", "proposta_appropriata_SI_NO_NA", "note_revisore"]


def markdown_report(rows, models, phase, manifest):
    lines = ["# Confronto modelli — UC-01", "", f"Fase: **{phase}**. Risultati di sviluppo, non validation né test.",
             "", "I conteggi indicano il comportamento della pipeline e NON la correttezza semantica. Compilare revisione_manuale.csv.",
             "", "| Modello | Casi | Errori/segnalazioni | Popup | Tempo medio (s, casi eseguiti) |",
             "|---|---:|---:|---:|---:|"]
    for m in models:
        sel = [r for r in rows if r["modello"] == m]
        valid = [r for r in sel if r["stato"] != "ERRORE" and isinstance(r["tempo_s"], (int, float))]
        avg = round(sum(r["tempo_s"] for r in valid)/len(valid),2) if valid else "—"
        lines.append(f"| {m} | {len(sel)} | {sum(r['stato']!='ESEGUITO' for r in sel)} | {sum(r['popup']=='SI' for r in sel)} | {avg} |")
    lines.extend(["", "## Lettura del risultato", "",
      "- La differenza tra 'popup' e 'candidato corretto' è essenziale: un popup può essere semanticamente errato.",
      "- Controllare separatamente estrazione, tipo, intenzione, gate Z e scelta del selettore.",
      "- JSON vincolato/non valido o errori server sono problemi di compatibilità della pipeline, non prova di incapacità linguistica.",
      "- In questa prova tutti i modelli ricevono gli stessi prompt e parametri, senza ottimizzazioni per famiglia.",
      "- Tutti i modelli usano il medesimo runtime aggiornato CPU; la demo originale non viene sostituita.",
      "- Le misure di tempo riguardano questo Mac Intel, non uno smartphone Android.",
      "", "## Riproducibilità", "",
      "- Endpoint temporaneo: 127.0.0.1:8091.",
      "- temperature=0; seed=42; max_tokens=350; contesto server=4096; CPU-only.",
      f"- Manifest: `manifest.json`; codice congelato sha256: `{manifest['sha256_demo_core']}`.",
      "- Nessuna scrittura su note, attività, calendario o servizi cloud. Vengono creati soltanto questi file di report.",
      "", "## Risultati per nota", ""])
    for cas in dict.fromkeys(x["caso"] for x in rows):
        lines.append(f"### {cas}")
        lines.append("")
        for r in [r for r in rows if r["caso"]==cas]:
            lines.append(f"- **{r['modello']}**: {r['frammenti']} frammenti, {r['candidati']} candidati; "
                         f"popup: {r['popup']} ({r['popup_tipo']}, «{r['popup_testo']}»); "
                         f"{r['tempo_s']} s; stato={r['stato']}" +
                         (f" — {r['errori']}" if r['errori'] else ""))
        lines.append("")
    return "\n".join(lines) + "\n"


def run(args):
    cases = read_json(ROOT / "casi" / ("fase1.json" if args.fase == "1" else "fase2.json"))["casi"]
    models = [m.strip() for m in args.modelli.split(",") if m.strip()]
    if not models or any(m not in MODELS for m in models):
        raise ValueError("Modelli disponibili: " + ", ".join(MODELS))
    if len(set(models)) != len(models):
        raise ValueError("Non ripetere lo stesso modello")
    # Port 8091 deve essere libero: non terminare server avviati da altre applicazioni.
    try:
        get_json(f"http://127.0.0.1:{PORT}/health")
    except Exception:
        pass
    else:
        raise RuntimeError(f"La porta {PORT} e' gia' occupata. Chiudi il server su questa porta e riprova.")
    binary=server_bin()
    model_paths={m: find_model(m) for m in models}
    sys.path.insert(0, str(ROOT / "pipeline_demo"))
    from demo_core import analyze_note, request_constrained
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    out=ROOT / "risultati" / (f"fase{args.fase}_{stamp}")
    out.mkdir(parents=True, exist_ok=False)
    detail=out/"dettagli"; detail.mkdir()
    sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest={
        "fase":args.fase,"casi":[c["id"] for c in cases], "modelli":models,
        "modelli_gguf":{k:{"file":str(v),"bytes":v.stat().st_size,"sha256":sha(v),
                          "origine":MODELS[k]["provenienza"]} for k,v in model_paths.items()},
        "runtime_llama":str(binary), "runtime_build": "", "riferimenti_temporali":"fissi_per_caso",
        "sha256_demo_core":sha(ROOT/"pipeline_demo"/"demo_core.py"),
        "sha256_prompts":{
            k:sha(ROOT/"pipeline_demo"/k) for k in [
            "frozen/xc_z/experiment_controls.py","frozen/xc_z/run_pipeline_bc.py",
            "frozen/xc_z/constrained_api.py", "frozen/selector/frozen_selector.py"]},
        "max_tokens":350, "temperature":0, "seed":42,"timeout_per_chiamata_s":240,
        "scritture_persistenti_su_dati_utente":0, "gold_nei_prompt":False,
        "esito_qualita_semantica":"non_ancora_revisionato"
    }
    try:
        rev=subprocess.run(["git", "-C", str(ROOT/"runtime"/"llama.cpp"), "rev-parse", "HEAD"],
                           capture_output=True,text=True,timeout=8)
        manifest["runtime_build"]=rev.stdout.strip() if rev.returncode==0 else "unknown"
    except Exception:
        pass
    write_json(out/"manifest.json",manifest)
    results=[]
    for model in models:
        print("\n=== Modello: " + model + " ===",flush=True)
        process, fh=launch_server(binary,model_paths[model],out/(model+"_llama.log"))
        try:
            try:
                name=wait_server(process)
                print("Caricato:", name,flush=True)
            except Exception as exc:
                reason="AVVIO_SERVER: " + str(exc)
                print("ERRORE:", reason,flush=True)
                for case in cases:
                    results.append(make_row(case,model,None,reason))
                continue
            for n,case in enumerate(cases,1):
                trace=[]
                def traced(call_args, system, user):
                    resp=request_constrained(call_args,system,user)
                    trace.append({"fase":"ESTRAZIONE" if not trace else "CLASSIFICAZIONE",
                                  "prompt_user":user,"risposta_json":resp.get("json"),
                                  "risposta_raw":resp.get("raw"),"errore":resp.get("error"),
                                  "parse_error":resp.get("parse_error"),
                                  "tempo_ms":resp.get("latency_ms")})
                    return resp
                print(f"[{n}/{len(cases)}] {case['id']}",end=" — ",flush=True)
                try:
                    res=analyze_note(case['nota'],model=name,now=datetime.fromisoformat(case['reference_datetime']),
                                     url=URL,timeout=240,request_fn=traced)
                    row=make_row(case,model,res)
                    write_json(detail/(model+"_"+case["id"]+".json"),
                               {"caso":case,"risultato":res,"traccia":trace})
                    print(f"{row['frammenti']} fr.; popup {row['popup']}; {row['tempo_s']}s", flush=True)
                except Exception as exc:
                    row=make_row(case,model,None,type(exc).__name__+": "+str(exc))
                    write_json(detail/(model+"_"+case["id"]+"_errore.json"),
                               {"caso":case,"errore":traceback.format_exc(),"traccia":trace})
                    print("ERRORE: " + str(exc),flush=True)
                results.append(row)
                persist(out,results,models,args.fase,manifest,cases)
        finally:
            stop_server(process,fh)
        persist(out,results,models,args.fase,manifest,cases)
    print("\nConfronto completato. File:",str(out),flush=True)
    return 0


def persist(out,rows,models,phase,manifest,cases):
    write_csv(out/"confronto.csv",rows,FIELDS)
    reviews=[]
    for r in rows:
        reviews.append({k:r.get(k,"") for k in REVIEW_FIELDS})
    write_csv(out/"revisione_manuale.csv",reviews,REVIEW_FIELDS)
    (out/"report.md").write_text(markdown_report(rows,models,phase,manifest),encoding="utf-8")


def main():
    p=argparse.ArgumentParser(description="Confronto UC-01 con modello locale su port 8091")
    p.add_argument("--fase",choices=["1","2"],default="1")
    p.add_argument("--modelli",default="qwen3-1.7b,qwen3.5-2b,lfm2.5-1.2b")
    args=p.parse_args()
    try: return run(args)
    except KeyboardInterrupt:
        print("Interrotto; risultati parziali salvati durante la prova.",file=sys.stderr)
        return 130
    except Exception as exc:
        print("ERRORE: "+str(exc),file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
