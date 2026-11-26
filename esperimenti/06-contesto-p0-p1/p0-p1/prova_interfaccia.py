#!/usr/bin/env python3
"""Paired P0/P1 experiment using exactly the same previously generated X2 output.
Only the X2->C2 literal quote projection changes; C2, Z, S2-V remain frozen.
"""
import argparse,csv,hashlib,json,sys,time,traceback
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent; BASE=ROOT/'selettore_s2_uc01_v01'
sys.path[:0]=[str(ROOT),str(BASE),str(BASE/'pipeline_demo'),str(BASE/'pipeline_demo/frozen/xc_z'),str(BASE/'pipeline_demo/frozen/selector')]
import demo_core
from experiment_controls import EXTRACT_X
from run_pipeline_bc import CONTRAST,stage1_check
from prova_c2 import request_c2,sha
from runtime_support import PORT,URL,find_model,get_json,launch_server,stop_server,wait_server
from prova_x0_x1 import read_cases,integrity,extract_comparison,save_csv,FIELDS,CFIELDS
from proiezione_contesto import project
VARS=('P0_ATOMICA','P1_CLAUSOLA')
EXTRA=['x2_original_quote','projection_details','input_x2_sha256','projection_differs_from_atomic']

def load_sources(dataset, evidence):
    cases=read_cases(dataset)
    raw=json.loads(evidence.read_text(encoding='utf-8'))
    by_id={x['case']['id']:x for x in raw['cases']}
    if len(by_id)!=len(cases):raise ValueError('Different case count in frozen X2 evidence')
    for case in cases:
        stored=by_id[case['id']]['case']
        if (stored['nota'],stored['reference_datetime'])!=(case['nota'],case['reference_datetime']):
            raise ValueError('Evidence and dataset differ: '+case['id'])
        for a in by_id[case['id']]['accepted']:
            s,e=a['action_span']
            if case['nota'][s:e]!=a['action_quote']:raise ValueError('Action offset not grounded')
            for ctx in a.get('context',[]):
                s,e=ctx['span']
                if case['nota'][s:e]!=ctx['quote']:raise ValueError('Context offset not grounded')
    return cases,by_id

def run_case(case, variant, accepted, model):
    projection=project(case['nota'],accepted,variant)
    quotes=[a['quote'] for a in projection]
    # Note: frozen stage1 may reject some valid but repeated span evidence; preserve that behavior.
    qv,err=stage1_check({'quotes':quotes},case['nota'])
    def dispatch(params,system,user):
        if system==EXTRACT_X:
            return {'raw':json.dumps({'quotes':quotes},ensure_ascii=False),'json':{'quotes':quotes},
                    'parse_error':None,'finish_reason':'offline_projection','usage':{},'latency_ms':0,'error':None}
        if system==CONTRAST:return request_c2(params,user)
        raise RuntimeError('Unexpected system prompt in frozen C2 protocol')
    res=demo_core.analyze_note(case['nota'],model=model,url=URL,timeout=240,
          now=datetime.fromisoformat(case['reference_datetime']),request_fn=dispatch)
    if res['quotes']!=qv:raise AssertionError('Stage1 validation mismatch')
    return res,projection,err

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--offline-only',action='store_true')
    ap.add_argument('--dataset',type=Path,default=ROOT/'note_test40_DIAGNOSTICO.json')
    ap.add_argument('--evidence',type=Path,default=ROOT/'estrazioni_x2_congelate.json')
    ap.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01')
    ap.add_argument('--out',type=Path);a=ap.parse_args()
    frozen=integrity();cases,by_id=load_sources(a.dataset,a.evidence)
    model=None;binary=None
    if not a.offline_only:
        model=find_model('qwen3-1.7b');binary=a.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
        if not binary.is_file():raise FileNotFoundError(binary)
        for k,path in [('model_sha256',model),('runtime_sha256',binary)]:
            if sha(path)!=frozen[k]:raise RuntimeError('Model/runtime mismatch: '+k)
        try:get_json(f'http://127.0.0.1:{PORT}/health')
        except Exception:pass
        else:raise RuntimeError('Local inference port occupied')
    out=a.out or ROOT/'risultati'/('proiezioni_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);(out/'dettagli').mkdir()
    manifest={'experiment':'X2 validated evidence P0 atomic versus P1 contiguous context clause',
      'nature':'projection/interface comparison, not extraction-only change',
      'source_x2_evidence_sha256':sha(a.evidence),'dataset_sha256':sha(a.dataset),
      'projection_code_sha256':sha(ROOT/'proiezione_contesto.py'),'runner_sha256':sha(Path(__file__)),
      'freeze_S2':frozen,'source_data_independent':False,'gold_loaded':False,'production_writes':False,
      'projection_policy':'bounded contiguous exact quote; no joining of noncontiguous spans',
      'model_calls':'only frozen C2; same X2 evidence for P0 and P1',
      'offline_only':a.offline_only,'note_count':len(cases)}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=[];cands=[];audit=[];proc=None;fh=None
    try:
        if not a.offline_only:
            proc,fh=launch_server(binary,model,out/'llama_server.log');model=wait_server(proc)
        for ix,case in enumerate(cases,1):
            for v in VARS:
                accepted=by_id[case['id']]['accepted'];proj=project(case['nota'],accepted,v)
                audit.append({'caso':case['id'],'variante':v,'nota':case['nota'],'n_actions_x2':len(accepted),
                              'projection_quotes':json.dumps([p['quote'] for p in proj],ensure_ascii=False),
                              'projection_details':json.dumps(proj,ensure_ascii=False)})
                if a.offline_only:continue
                print(f'[{ix}/{len(cases)}] {case["id"]} {v}',flush=True)
                try:
                    res,projection,err=run_case(case,v,accepted,model)
                    row,cr=extract_comparison(case,v,res)
                    row.update({'x2_original_quote':json.dumps([p['atomic'] for p in projection],ensure_ascii=False),
                       'projection_details':json.dumps(projection,ensure_ascii=False),
                       'input_x2_sha256':sha(a.evidence),
                       'projection_differs_from_atomic':sum(p['quote']!=p['atomic'] for p in projection)})
                    rows.append(row);cands.extend(cr)
                    (out/'dettagli'/f'{case["id"]}_{v}.json').write_text(json.dumps(
                      {'case':case,'variant':v,'projection':projection,'result':res,'evaluation':row,'candidates':cr},
                      ensure_ascii=False,indent=2),encoding='utf-8')
                except Exception as exc:
                    rows.append({'caso':case['id'],'nota':case['nota'],'variante':v,'errori_pipeline':f'{type(exc).__name__}: {exc}'})
                    (out/'dettagli'/f'{case["id"]}_{v}_ERRORE.txt').write_text(traceback.format_exc(),encoding='utf-8')
                save_csv(out/'confronto_note.csv',rows,FIELDS+EXTRA)
                save_csv(out/'confronto_candidati.csv',cands,CFIELDS)
        save_csv(out/'audit_proiezioni.csv',audit,['caso','variante','nota','n_actions_x2','projection_quotes','projection_details'])
    finally:
        if proc:stop_server(proc,fh)
    (out/'report.md').write_text('# Confronto P0/P1 su X2 congelato\n\n'+
        f'Note {len(cases)}; righe valutate {len(rows)}; solo audit {a.offline_only}.\n'+
        'Le metriche di correttezza richiedono valutazione umana; il gold non e stato letto.\n',encoding='utf-8')
    print('Risultati:',out)

if __name__=='__main__':main()
