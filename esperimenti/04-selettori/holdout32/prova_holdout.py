#!/usr/bin/env python3
"""Validazione holdout: baseline X0+C0+Z+S0 contro candidata X0+C2+Z+S1.
Un'unica estrazione X0 per nota; il GOLD non viene mai letto.
"""
import argparse,csv,hashlib,json,sys,traceback
from datetime import datetime
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'pipeline_demo/frozen/selector'))
from prova_c2 import run_pair, sha, C2, save_csv
from prova_s1_replay import select_s1
from runtime_support import find_model,launch_server,stop_server,wait_server,PORT,get_json,URL

FIELDS=['caso','gruppo','nota','n_frammenti','baseline_popup','baseline_testo','baseline_kind','baseline_intent','candidata_popup','candidata_testo','candidata_kind','candidata_intent','baseline_errori','candidata_errori','baseline_tempo_logico_s','candidata_tempo_logico_s','valutazione_baseline','valutazione_candidata','motivazione_revisore']
FRAGS=['caso','frammento','c0_kind','c0_intent','c2_kind','c2_intent','c0_z','c2_z','c0_selected','s1_selected','s1_veto','gold_kind_MANUALE','gold_intent_MANUALE','commento_MANUALE']

def check_frozen():
 frozen=json.loads((BASE/'FREEZE.json').read_text(encoding='utf-8'))
 for name,expected in frozen['file_hashes_sha256'].items():
  actual=sha(BASE/name)
  if actual!=expected: raise RuntimeError(f'FILE CONGELATO MODIFICATO: {name} {actual} != {expected}')
 if hashlib.sha256(C2.encode()).hexdigest()!=frozen['prompt_C2_runtime_sha256']:
  raise RuntimeError('Prompt C2 alterato')
 data=json.loads((BASE/'holdout32.json').read_text(encoding='utf-8'))['casi']
 if len(data)!=32 or len({x['id'] for x in data})!=32:raise RuntimeError('Holdout non integro')
 if sha(BASE/'holdout32.json')!=frozen['holdout_sha256']:raise RuntimeError('Holdout modificato dopo il freeze')
 return frozen,data

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,default=Path.home()/'Desktop/confronto_slm_uc01_v01');args=ap.parse_args()
 frozen,cases=check_frozen()
 model_path=find_model('qwen3-1.7b'); runtime=args.base.expanduser()/'runtime/llama.cpp/build/bin/llama-server'
 if not runtime.is_file():raise FileNotFoundError(runtime)
 # Model/runtime pins derive from the successful previous S0/S1 run.
 for label,path in [('model_sha256',model_path),('runtime_sha256',runtime)]:
  actual=sha(path)
  if actual!=frozen[label]:raise RuntimeError(f'{label} diverso dal precedente: {actual}')
 try:get_json(f'http://127.0.0.1:{PORT}/health')
 except Exception:pass
 else:raise RuntimeError('La porta 8091 è già occupata; chiudi il server prima del test')
 from datetime import datetime as DT
 out=BASE/'risultati'/('holdout_baseline_vs_candidata_'+DT.now().strftime('%Y%m%d_%H%M%S'))
 out.mkdir(parents=True,exist_ok=False);(out/'dettagli').mkdir()
 manifest={'studio':'Holdout sintetico UC01 v01','configurazioni':{'baseline':'X0+C0+Z+S0','candidata':'X0+C2+Z+S1'},'holdout_n':32,'freeze':frozen,'model_sha256':sha(model_path),'runtime_sha256':sha(runtime),'writes_performed':False,'gold_loaded_during_inference':False,'independent_from_development24':True,'external_real_world_generalization':False}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 rows=[];frags=[]
 proc,fh=launch_server(runtime,model_path,out/'llama_server.log')
 try:
  model=wait_server(proc)
  for i,case in enumerate(cases,1):
   print(f'[{i:02d}/32] {case["id"]}',flush=True)
   try:
    results,traces=run_pair(case['nota'],datetime.fromisoformat(case['reference_datetime']),model,URL)
    b=results['C0'];c=results['C2'];s1diags,s1=select_s1(case,c)
    sel0=b.get('selected') or {};sel1=next((x for x in c['candidates'] if s1 and x['id']==s1['candidate_id']),{})
    row={'caso':case['id'],'gruppo':case['gruppo'],'nota':case['nota'],'n_frammenti':len(b['quotes']),
      'baseline_popup':'SI' if sel0 else 'NO','baseline_testo':sel0.get('evidence',''),'baseline_kind':sel0.get('kind',''),'baseline_intent':sel0.get('intent',''),
      'candidata_popup':'SI' if sel1 else 'NO','candidata_testo':sel1.get('evidence',''),'candidata_kind':sel1.get('kind',''),'candidata_intent':sel1.get('intent',''),
      'baseline_errori':' | '.join(b.get('errors',[])),'candidata_errori':' | '.join(c.get('errors',[])),
      'baseline_tempo_logico_s':round(b['latency_ms']/1000,2),'candidata_tempo_logico_s':round(c['latency_ms']/1000,2),
      'valutazione_baseline':'','valutazione_candidata':'','motivazione_revisore':''}
    rows.append(row)
    map0={x['evidence']:x for x in b['candidates']};map2={x['evidence']:x for x in c['candidates']}
    diags_by_id={x['candidate_id']:x for x in s1diags}
    for q in b['quotes']:
     a=map0.get(q,{});d=map2.get(q,{});sd=diags_by_id.get(d.get('id'),{})
     frags.append({'caso':case['id'],'frammento':q,'c0_kind':a.get('kind',''),'c0_intent':a.get('intent',''),
       'c2_kind':d.get('kind',''),'c2_intent':d.get('intent',''),'c0_z':a.get('sandbox_gate',''),'c2_z':d.get('sandbox_gate',''),
       'c0_selected':'SI' if a.get('selected') else 'NO','s1_selected':'SI' if sd.get('new_popup') else 'NO',
       's1_veto':' | '.join(sd.get('s1_veto_reasons',[])),
       'gold_kind_MANUALE':'','gold_intent_MANUALE':'','commento_MANUALE':''})
    (out/'dettagli'/(case['id']+'.json')).write_text(json.dumps({'case':case,'C0_S0':b,'C2_S0':c,'S1_diagnostics':s1diags,'trace':traces},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('  BASELINE:',sel0.get('evidence','—'),'| CANDIDATA:',sel1.get('evidence','—'),flush=True)
   except Exception as exc:
    msg=traceback.format_exc()
    rows.append({'caso':case['id'],'gruppo':case['gruppo'],'nota':case['nota'],'baseline_errori':str(exc),'candidata_errori':str(exc)})
    (out/'dettagli'/(case['id']+'_ERRORE.txt')).write_text(msg,encoding='utf-8')
   save_csv(out/'confronto_note.csv',rows,FIELDS)
   save_csv(out/'revisione_note.csv',rows,FIELDS)
   save_csv(out/'confronto_frammenti.csv',frags,FRAGS)
 finally:stop_server(proc,fh)
 report=['# Holdout sintetico — baseline vs candidata','',f'Note: {len(rows)}',f'Frammenti: {len(frags)}',
         f'Popup baseline: {sum(x.get("baseline_popup")=="SI" for x in rows)}',f'Popup candidata: {sum(x.get("candidata_popup")=="SI" for x in rows)}',
         f'Note con selezione differente: {sum(x.get("baseline_testo","")!=x.get("candidata_testo","") for x in rows)}',
         '', 'Questi conteggi NON sono accuratezza: compilare la revisione manuale prima della decisione.','I casi sono nuovi ma sintetici, non validazione su note reali in produzione.','']
 (out/'report.md').write_text('\n'.join(report),encoding='utf-8')
 print('RISULTATI:',out,flush=True)
if __name__=='__main__':main()
