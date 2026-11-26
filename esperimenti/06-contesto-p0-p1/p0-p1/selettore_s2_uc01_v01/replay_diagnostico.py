#!/usr/bin/env python3
"""Offline: ricostruisce i candidati già inferiti, non usa il gold.
La ricostruzione HOLD non contiene score originali salvati: vengono ricalcolati
con gli stessi selettori congelati a partire da quote, etichette e Z.
"""
import csv,sys,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'pipeline_demo/frozen/selector'))
from selettore_s2 import choose_variant
VARIANTS=('S1','S2-V','S2-R','S2-VR')
def readcsv(name):
 with (BASE/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def records():
 dev=readcsv('diagnostica_development24.csv')
 grouped={}
 for row in dev:
  k=('DEV',row['caso']);grouped.setdefault(k,[]).append({'review_id':row['caso']+'__'+row['candidate_id'],'scenario_id':row['caso'],'candidate_id':row['candidate_id'],'note_originale':'','citazione':row['frammento'],'tipo_predetto':row['kind'],'intenzione_predetta':row['intent'],'decisione_sandbox':row['z_decision'],'popup_mostrato':'1' if row['s1_selected']=='SI' else '0'})
 # Development original notes are recovered from the fixed development JSON.
 data=json.loads((BASE/'development24.json').read_text(encoding='utf-8'))
 cases=data['casi'] if isinstance(data,dict) else data
 notes={x['id']:x['nota'] for x in cases}
 for (_,case),group in grouped.items():
  if case not in notes:raise ValueError('Nota non trovata: '+case)
  for rec in group:rec['note_originale']=notes[case]
 holdnotes={r['caso']:r['nota'] for r in readcsv('diagnostica_holdout32_note.csv')}
 rows=readcsv('diagnostica_holdout32_frammenti.csv')
 ids={}
 for r in rows:
  case=r['caso'];index=ids.get(case,0)+1;ids[case]=index
  grouped.setdefault(('HOLD',case),[]).append({'review_id':case+'__C'+str(index),'scenario_id':case,'candidate_id':'C'+str(index),'note_originale':holdnotes[case],'citazione':r['frammento'],'tipo_predetto':r['c2_kind'],'intenzione_predetta':r['c2_intent'],'decisione_sandbox':r['c2_z'],'popup_mostrato':'1' if r['s1_selected']=='SI' else '0'})
 return grouped

def run(output):
 output.mkdir(parents=True,exist_ok=True)
 cases=records(); result=[]; candidates=[]
 for (dataset,case),recs in sorted(cases.items()):
  row={'dataset':dataset,'caso':case,'nota':recs[0]['note_originale'],'n_candidati':len(recs)}
  for variant in VARIANTS:
   ds,winner=choose_variant(recs,variant)
   row[variant+'_testo']=winner['text'] if winner else ''
   row[variant+'_id']=winner['candidate_id'] if winner else ''
   for d in ds:
    candidates.append({'dataset':dataset,'caso':case,'variante':variant,'candidate_id':d['candidate_id'],'testo':d['text'],'kind':d['kind'],'intent':d['intent'],'z':d['gate_decision'],'eleggibile':d['eligible'],'score':d['score'],'selezionato':d['new_popup'],'veto':'|'.join(d.get('s2_veto_reasons',[])),'ranking':'|'.join(d.get('s2_ranking_reasons',[])),'reject_reasons':'|'.join(d['reject_reasons'])})
  row['cambiamento_V']=row['S1_id']!=row['S2-V_id']
  row['cambiamento_R']=row['S1_id']!=row['S2-R_id']
  row['cambiamento_VR']=row['S1_id']!=row['S2-VR_id']
  row['valutazione_manuale']='';row['motivazione_manuale']=''
  result.append(row)
 def save(name,rows):
  with (output/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 save('diagnostico_note.csv',result);save('diagnostico_candidati.csv',candidates)
 lines=['# Replay diagnostico S1 / S2-V / S2-R / S2-VR','', 'Nessuna inferenza: risultati ricostruiti dai CSV precedenti. Set noti, NON validazione indipendente.','']
 for dataset in ('DEV','HOLD'):
  subset=[x for x in result if x['dataset']==dataset]
  lines.append(f'## {dataset}: {len(subset)} note')
  for v in VARIANTS:lines.append(f'- {v}: {sum(bool(x[v+"_id"]) for x in subset)} popup')
  for v in VARIANTS[1:]:lines.append(f'- {v}: {sum(x["S1_id"]!=x[v+"_id"] for x in subset)} note cambiate rispetto a S1')
  lines.append('')
  for x in subset:
   if any(x['S1_id']!=x[v+'_id'] for v in VARIANTS[1:]):
    lines.append(f'- {x["caso"]}: S1 «{x["S1_testo"]}»; V «{x["S2-V_testo"]}»; R «{x["S2-R_testo"]}»; VR «{x["S2-VR_testo"]}»')
  lines.append('')
 lines += ['## Limiti', '- Se X0 non estrae l’azione, S2 non può recuperarla.', '- Un solo popup per nota: non misura il recall di tutte le azioni.', '- Le metriche di correttezza richiedono revisione manuale; i conteggi di popup non sono accuratezza.', '']
 (output/'report_diagnostico.md').write_text('\n'.join(lines),encoding='utf-8')
 return result
if __name__=='__main__':
 out=BASE/'risultati'/'diagnostico'; rows=run(out);print('Replay:',len(rows),'note; output:',out)
