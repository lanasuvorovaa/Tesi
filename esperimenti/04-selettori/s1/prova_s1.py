#!/usr/bin/env python3
"""UC-01 controlled S0/S1 test: one X0+C2+Z execution per note; replay S only."""
import csv, json, hashlib, sys, traceback
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'pipeline_demo'))
sys.path.insert(0,str(BASE/'pipeline_demo/frozen/xc_z'))
sys.path.insert(0,str(BASE/'pipeline_demo/frozen/selector'))
from demo_core import analyze_note
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST
from prova_c2 import request_c2, cases, sha
from runtime_support import PORT,URL,find_model,get_json,launch_server,wait_server,stop_server
from selettore_s1 import choose_s1

NOTE_COLS=['caso','nota','n_frammenti','s0_popup','s0_testo','s1_popup','s1_testo','s0_id','s1_id','esito_manuale','note_revisione','errori']
CAND_COLS=['caso','frammento','candidate_id','kind','intent','z_decision','s0_eligible','s1_eligible','s0_selected','s1_selected','s1_veto_reasons','s0_reject_reasons','s1_reject_reasons','commento_manuale']

def save_csv(path,rows,columns):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)

def compare_one(case,result):
    # No additional X, C or Z calls; only the S decision is replayed.
    candidates=result['candidates']
    records=[]
    for c in candidates:
        records.append({'review_id':case['id']+'__'+c['id'],'scenario_id':case['id'],'candidate_id':c['id'],
            'note_originale':case['nota'],'citazione':c['evidence'],'tipo_predetto':c['kind'],
            'intenzione_predetta':c['intent'],'decisione_sandbox':c['sandbox_gate'],
            'popup_mostrato':'1' if c['selected'] else '0'})
    diagnostics,s1=choose_s1(records)
    old=result.get('selected') or {}
    s1_id=s1['candidate_id'] if s1 else ''
    row={'caso':case['id'],'nota':case['nota'],'n_frammenti':len(result['quotes']),
        's0_popup':'SI' if old else 'NO','s0_testo':old.get('evidence',''),
        's1_popup':'SI' if s1 else 'NO','s1_testo':s1['text'] if s1 else '',
        's0_id':old.get('id',''),'s1_id':s1_id,'esito_manuale':'','note_revisione':'',
        'errori':' | '.join(result.get('errors',[]))}
    details=[]
    for c,d in zip(candidates,diagnostics):
        # Verify S0 state has not changed; identical Z and classifications by construction.
        details.append({'caso':case['id'],'frammento':c['evidence'],'candidate_id':c['id'],
            'kind':c['kind'],'intent':c['intent'],'z_decision':c['sandbox_gate'],
            's0_eligible':str(c['eligible']),'s1_eligible':str(d['eligible']),
            's0_selected':'SI' if c['selected'] else 'NO','s1_selected':'SI' if d['new_popup'] else 'NO',
            's1_veto_reasons':'|'.join(d['s1_veto_reasons']),
            's0_reject_reasons':'|'.join(c['selector_reasons']),
            's1_reject_reasons':'|'.join(d['reject_reasons']),
            'commento_manuale':''})
    return row,details

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01')
    a=p.parse_args();data=cases(); model_path=find_model('qwen3-1.7b')
    binary=a.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
    if not binary.is_file():raise FileNotFoundError(binary)
    try:get_json('http://127.0.0.1:'+str(PORT)+'/health')
    except Exception:pass
    else:raise RuntimeError('Porta 8091 occupata')
    from prova_c2 import C2
    manifest={'esperimento':'S0 vs S1 su X0+C2+Z, development 24',
              'unica_modifica':'selettore S; X0, C2, Z invariati',
              'dataset_sha256':sha(BASE/'development24.json'),
              'selector_s0_sha256':sha(BASE/'pipeline_demo/frozen/selector/frozen_selector.py'),
              'selector_s1_sha256':sha(BASE/'selettore_s1.py'),
              'prompt_C2_sha256':hashlib.sha256(C2.encode()).hexdigest(),
              'model_sha256':sha(model_path),'runtime_sha256':sha(binary),
              'parameters':{'temperature':0,'seed':42,'max_tokens':350,'context':4096,'ngl':0,'threads':6},
              'no_writes':True,'independent_validation':False}
    out=BASE/'risultati'/('s0_vs_s1_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    out.mkdir(parents=True,exist_ok=False);(out/'dettagli').mkdir()
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    rows=[];candrows=[]
    proc,fh=launch_server(binary,model_path,out/'llama_server.log')
    try:
        model=wait_server(proc)
        for i,case in enumerate(data,1):
            print(f'[{i:02}/24] {case["id"]}',flush=True)
            try:
                def dispatch(args,system,user):
                    if system==EXTRACT_X:
                        from constrained_api import request_constrained
                        return request_constrained(args,system,user)
                    if system==CONTRAST:return request_c2(args,user)
                    raise RuntimeError('Prompt inatteso')
                result=analyze_note(case['nota'],model=model,url=URL,timeout=240,now=datetime.fromisoformat(case['reference_datetime']),request_fn=dispatch)
                row,details=compare_one(case,result)
                rows.append(row);candrows.extend(details)
                (out/'dettagli'/(case['id']+'.json')).write_text(json.dumps({'case':case,'result':result,'s0_s1':row,'candidate_comparison':details},indent=2,ensure_ascii=False),encoding='utf-8')
                print('  S0:',row['s0_testo'] or 'nessuno','| S1:',row['s1_testo'] or 'nessuno',flush=True)
            except Exception:
                msg=traceback.format_exc();rows.append({'caso':case['id'],'nota':case['nota'],'errori':msg.splitlines()[-1]})
                (out/'dettagli'/(case['id']+'_errore.txt')).write_text(msg,encoding='utf-8')
            save_csv(out/'confronto_note.csv',rows,NOTE_COLS)
            save_csv(out/'revisione_note.csv',rows,NOTE_COLS)
            save_csv(out/'confronto_candidati.csv',candrows,CAND_COLS)
            save_csv(out/'revisione_candidati.csv',candrows,CAND_COLS)
    finally:stop_server(proc,fh)
    changes=[r for r in rows if r.get('s0_id')!=r.get('s1_id')]
    report=['# Esperimento selettore S0–S1','', 'S0 e S1 valutati sugli stessi candidati prodotti una volta da X0+C2+Z.','',
            f'- Note: {len(rows)}; candidati: {len(candrows)}',
            f'- Popup S0: {sum(r.get("s0_popup")=="SI" for r in rows)}',
            f'- Popup S1: {sum(r.get("s1_popup")=="SI" for r in rows)}',
            f'- Note con selezione differente: {len(changes)}','',
            '## Modifiche (non sono giudizi di correttezza)','']
    for r in changes:report.append(f'- {r["caso"]}: S0 «{r.get("s0_testo","")}» → S1 «{r.get("s1_testo","")}»')
    report += ['', 'Le etichette di correttezza dei popup vanno annotate manualmente.','Le 24 note sono development, non validation indipendente.']
    (out/'report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print('Risultati:',out)
if __name__=='__main__':main()
