#!/usr/bin/env python3
"""UC-01: full pipeline comparison on the frozen development 24.

Baseline: Qwen3-1.7B, original extraction X0/classification C0.
Candidate: Qwen3.5-2B, experimental extraction X1, same C0/Z/selector.

This is a candidate SYSTEM comparison, not an isolated model comparison.
Nothing writes to tasks/calendar. Reports only are stored locally.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, sys, time, traceback
from datetime import datetime
from pathlib import Path
from urllib import error as urlerror

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'pipeline_demo'))
sys.path.insert(0,str(ROOT/'pipeline_demo'/'frozen'/'xc_z'))
sys.path.insert(0,str(ROOT/'pipeline_demo'/'frozen'/'selector'))

from confronta import (PORT, URL, find_model, launch_server, wait_server, stop_server,
                      get_json, make_row, FIELDS)
from demo_core import analyze_note
from constrained_api import request_constrained, EXTRACTION_SCHEMA
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST
from run_notes import call_server
from semantic_core_v6 import parse_json

X1=(ROOT/'x1_prompt.txt').read_text(encoding='utf-8').rstrip('\n')
MODELS=[('qwen3-1.7b','X0+C0+Z+S'),('qwen3.5-2b','X1+C0+Z+S')]
REVIEW_FIELDS=['caso','nota','modello','variante','frammenti_testo','etichette','popup_testo',
               'tipo_e_intenzione_corrette_SI_NO','elementi_separati_SI_NO',
               'proposta_appropriata_SI_NO_NA','errore_piu_grave','note_revisore']


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as fd:
        for part in iter(lambda:fd.read(4*1024*1024),b''):h.update(part)
    return h.hexdigest()


def save_json(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def save_csv(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as fd:
        wr=csv.DictWriter(fd,fieldnames=fields,extrasaction='ignore')
        wr.writeheader();wr.writerows(rows)


def x1_call(args,user):
    req={'model':args.model,
         'messages':[{'role':'system','content':X1},{'role':'user','content':user}],
         'temperature':0,'seed':42,'max_tokens':args.max_tokens,'stream':False,
         'chat_template_kwargs':{'enable_thinking':False},
         'response_format':{'type':'json_schema','json_schema':
           {'name':'atomic_quotes','strict':True,'schema':EXTRACTION_SCHEMA}}}
    start=time.perf_counter()
    try:
        raw,finish,usage=call_server(args.url,req,args.timeout)
        parsed,error=parse_json(raw)
        return {'raw':raw,'json':parsed,'parse_error':error,'finish_reason':finish,
                'usage':usage,'latency_ms':round((time.perf_counter()-start)*1000,2),'error':None}
    except Exception as exc:
        return {'raw':None,'json':None,'parse_error':None,'finish_reason':None,'usage':{},
                'latency_ms':round((time.perf_counter()-start)*1000,2),
                'error':type(exc).__name__+': '+str(exc)}


def routed_call(key,args,system,user,trace):
    if system not in (EXTRACT_X, CONTRAST):
        raise RuntimeError('Prompt inatteso: nessun cambiamento tacito alla pipeline')
    xstage=(system==EXTRACT_X)
    if key=='qwen3.5-2b' and xstage:
        response=x1_call(args,user)
    else:
        response=request_constrained(args,system,user)
    trace.append({'fase':('X1' if key=='qwen3.5-2b' else 'X0') if xstage else 'C0',
                  'prompt_sha256':hashlib.sha256((X1 if key=='qwen3.5-2b' and xstage else system).encode()).hexdigest(),
                  'richiesta':user,'json':response.get('json'),'raw':response.get('raw'),
                  'errore':response.get('error'),'errore_parse':response.get('parse_error'),
                  'tempo_ms':response.get('latency_ms')})
    return response


def get_cases():
    data=json.loads((ROOT/'casi'/'development24.json').read_text(encoding='utf-8'))
    cases=data['casi']
    if len(cases)!=24 or len({c['id'] for c in cases})!=24:
        raise RuntimeError('Il pacchetto non contiene 24 note development uniche')
    if any(c['origine']!='development_24_frozen' for c in cases):
        raise RuntimeError('Dataset non autorizzato: soltanto development congelato')
    return cases


def report_md(rows,manifest):
    lines=['# Confronto UC-01 — Qwen3 baseline / Qwen3.5 con estrazione X1',
      '', '**Ambito:** 24 note di development già note. Non è validation indipendente.',
      '**Tipo di confronto:** sistemi candidati; cambiano modello **e** prompt di estrazione. Non attribuire eventuali differenze al solo modello.',
      '**Restano invariati:** classificazione C0, controlli Z, selettore S, schema JSON, parametri di decoding e dataset.',
      '', '| Sistema | Note elaborate | Errori/segnalazioni | Popup | Tempo medio inferenza (s) |',
      '|---|---:|---:|---:|---:|']
    for model,variant in MODELS:
        group=[r for r in rows if r['modello']==model]
        good=[r for r in group if r['stato']!='ERRORE' and isinstance(r['tempo_s'],(float,int))]
        avg=round(sum(r['tempo_s'] for r in good)/len(good),2) if good else '—'
        lines.append(f"| {model} ({variant}) | {len(group)} | {sum(r['stato']!='ESEGUITO' for r in group)} | {sum(r['popup']=='SI' for r in group)} | {avg} |")
    lines.extend(['','**Importante:** popup e conteggi NON sono misure di correttezza semantica; analizzare `revisione_manuale.csv` e i JSON dettagliati.',
      '', '## Risultati per nota',''])
    for case_id in manifest['casi']:
        lines.append('### '+case_id)
        lines.append('')
        for row in [r for r in rows if r['caso']==case_id]:
            lines.append(f"- **{row['modello']}**: {row['frammenti']} frammenti; etichette: {row['etichette'] or '—'}; "
                         f"popup: {row['popup']} ({row['popup_tipo'] or '—'}, «{row['popup_testo']}»); "
                         f"{row['tempo_s']} s; {row['stato']}"+(f"; {row['errori']}" if row['errori'] else ''))
        lines.append('')
    lines.extend(['## Criteri per la decisione','',
      '1. Controllare separatamente le attività e gli eventi e la loro intenzione, soprattutto negazioni e azioni completate.',
      '2. Controllare che un segmento citato contenga elementi sufficienti per essere autonomo; segnalare i casi con più azioni fuse.',
      '3. La data vaga del caso UC01-MAIN-052 richiede chiarimento nella politica desiderata: non considerare corretta una proposta operativa non verificata.',
      '4. Un solo popup non significa che il secondo elemento della nota sia perso: aprire i candidati e le tracce.',
      '5. Le 24 note comprendono casi già usati per scegliere X1, perciò non sono indipendenti dalla scelta del prompt.',
      '', '## Riproducibilità','',
      f"- Server: 127.0.0.1:{PORT} (solo locale), llama.cpp CPU; modello caricato sequenzialmente.",
      '- `temperature=0`, `seed=42`, `max_tokens=350`, contesto=4096, JSON schema vincolato.',
      '- Prompt X1 identico a quello del precedente diagnostico (SHA256 nel manifest).',
      '- Nessuna scrittura su calendario o attività; vengono salvati soltanto questi risultati.',
      '- Le prestazioni sul Mac non sono una misura delle prestazioni su Android.'])
    return '\n'.join(lines)+'\n'


def persist(out,rows,manifest):
    save_csv(out/'confronto.csv',rows,FIELDS+['variante'])
    reviews=[{key:r.get(key,'') for key in REVIEW_FIELDS} for r in rows]
    save_csv(out/'revisione_manuale.csv',reviews,REVIEW_FIELDS)
    (out/'report.md').write_text(report_md(rows,manifest),encoding='utf-8')


def run(base):
    cases=get_cases()
    binary=base/'runtime'/'llama.cpp'/'build'/'bin'/'llama-server'
    if not binary.is_file():
        raise FileNotFoundError('Runtime non trovato: '+str(binary)+'; riutilizza il confronto precedente')
    venv=base/'.venv'/'bin'/'python'
    model_paths={key:find_model(key) for key,_ in MODELS}
    try:
        get_json('http://127.0.0.1:'+str(PORT)+'/health')
    except Exception:pass
    else:raise RuntimeError('Porta 8091 già occupata: chiudi il server avviato da un altro programma')
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
    out=ROOT/'risultati'/('development24_'+stamp)
    out.mkdir(parents=True,exist_ok=False)
    (out/'dettagli').mkdir()
    manifest={
      'scope':'development_24_only','casi':[c['id'] for c in cases],
      'sistemi':{key:variant for key,variant in MODELS},
      'parametri':{'temperature':0,'seed':42,'max_tokens':350,'ctx':4096,'ngl':0,'threads':6},
      'binary':str(binary),'binary_sha256':sha256(binary),
      'modelli':{key:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha256(p)} for key,p in model_paths.items()},
      'prompt_X0_sha256':hashlib.sha256(EXTRACT_X.encode()).hexdigest(),
      'prompt_X1_sha256':hashlib.sha256(X1.encode()).hexdigest(),
      'prompt_C0_sha256':hashlib.sha256(CONTRAST.encode()).hexdigest(),
      'codice_demo_sha256':sha256(ROOT/'pipeline_demo'/'demo_core.py'),
      'dataset_sha256':sha256(ROOT/'casi'/'development24.json'),
      'nota_confronto':'cambiano modello e prompt X; questo non misura il solo effetto del modello',
      'nesuna_scrittura_persistente':True,
    }
    save_json(out/'manifest.json',manifest)
    rows=[]
    for key,variant in MODELS:
        print('\n=== '+key+' · '+variant+' ===',flush=True)
        proc,logfile=launch_server(binary,model_paths[key],out/(key+'_llama.log'))
        try:
            model_id=wait_server(proc)
            for n,case in enumerate(cases,1):
                print(f'[{n}/24] {case["id"]}',end=' — ',flush=True)
                trace=[]
                try:
                    res=analyze_note(case['nota'],model=model_id,now=datetime.fromisoformat(case['reference_datetime']),
                                     url=URL,timeout=240,request_fn=lambda a,s,u:routed_call(key,a,s,u,trace))
                    row=make_row(case,key,res)
                    save_json(out/'dettagli'/f'{key}_{case["id"]}.json',
                              {'caso':case,'variante':variant,'risultato':res,'traccia':trace})
                    print(f'{row["frammenti"]} frammenti; popup {row["popup"]}; {row["tempo_s"]} s',flush=True)
                except Exception as exc:
                    row=make_row(case,key,None,type(exc).__name__+': '+str(exc))
                    save_json(out/'dettagli'/f'{key}_{case["id"]}_errore.json',
                              {'caso':case,'variante':variant,'errore':traceback.format_exc(),'traccia':trace})
                    print('ERRORE: '+str(exc),flush=True)
                row['variante']=variant
                rows.append(row)
                persist(out,rows,manifest)
        finally:
            stop_server(proc,logfile)
    print('\nConfronto completato. Report: '+str(out),flush=True)
    return 0


def main():
    ap=argparse.ArgumentParser(description='Confronto end-to-end su development UC-01')
    ap.add_argument('--base',type=Path,default=Path.home()/'Desktop'/'confronto_slm_uc01_v01',
                    help='Cartella del confronto originale con runtime/.venv')
    ns=ap.parse_args()
    try:return run(ns.base)
    except KeyboardInterrupt:print('Interrotto. Output intermedi disponibili nella cartella risultati.',file=sys.stderr);return 130
    except Exception as exc:print(f'ERRORE {type(exc).__name__}: {exc}',file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
