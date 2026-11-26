#!/usr/bin/env python3
"""Replay stored X2-v01 raw model output, no inference, no downstream execution."""
import csv,json,argparse,zipfile
from pathlib import Path
from collections import Counter
from x2_core import align_x2,strip_v01_spans,locate
ROOT=Path(__file__).resolve().parent

def replay(src,out):
 out.mkdir(parents=True,exist_ok=True)
 rows=[];errors=Counter();total_raw=0;total_accepted=0;notes=0;literal=0
 with zipfile.ZipFile(src) as z:
  members=sorted(n for n in z.namelist() if n.endswith('_X2.json') and '/dettagli/' in n)
  for member in members:
   d=json.loads(z.read(member));case=d['case'];trace=d['structured_x2'];raw=trace.get('raw')
   transformed=strip_v01_spans(raw);accepted,errs=align_x2(transformed,case['nota'])
   actions=raw.get('actions',[]) if isinstance(raw,dict) and isinstance(raw.get('actions'),list) else []
   notes+=1;total_raw+=len(actions);total_accepted+=len(accepted);errors.update(errs)
   for idx,a in enumerate(actions):
    quote=a.get('action_quote') if isinstance(a,dict) else None
    _,why=locate(case['nota'],quote)
    if why is None:literal+=1
    rows.append({'caso':case['id'],'indice_azione':idx+1,'citazione':quote or '',
      'presenza_univoca':why is None,'errore_citazione':why or '',
      'accettata_dopo_allineamento':any(x['id']==a.get('id') for x in accepted) if isinstance(a,dict) else False,
      'errori_nota':' | '.join(errs)})
  if notes != 40:raise RuntimeError(f'Expected 40 stored X2 cases; found {notes}')
 with (out/'audit_replay_azioni.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary={'source':str(src.name),'mode':'offline_v01_raw_to_v02_alignment; NO MODEL INFERENCE','notes':notes,
          'actions_raw':total_raw,'actions_with_unique_literal_quote':literal,
          'accepted_actions_strict_v02':total_accepted,'rejected_actions':total_raw-total_accepted,
          'error_counts':dict(errors),'note':'Old v01 output retains self-referential relations and hallucinated/misassigned context; this does not predict v02 inference performance.'}
 (out/'sintesi_replay.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--out',type=Path,default=ROOT/'replay_offline');a=p.parse_args();replay(a.zip,a.out)
