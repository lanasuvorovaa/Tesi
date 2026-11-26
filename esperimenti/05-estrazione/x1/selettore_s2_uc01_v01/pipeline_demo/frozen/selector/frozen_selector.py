#!/usr/bin/env python3
"""Frozen heuristic selector: no model, no gold in selection. Italian development-only diagnostic."""
import csv, json, re, argparse, pathlib, collections
ROOT=pathlib.Path(__file__).resolve().parent
ACTION_WORDS=r'(?:devo|deve|dovrei|dobbiamo|bisogna|ricordarmi|vorrei|potrei|voglio|intendevo|inviare|mandare|chiamare|sentire|prenotare|controllare|ritirare|avvisare|imballare|preparare|organizzare|aggiornare|scrivere|consegnare|pagare|fare|comprare|restituire|incontrare|verificare|portare|spedire|andare|prenota|manda|controlla|avvisa|ritira|scrivi)'
EVENT_WORDS=r'(?:visita|riunione|appuntamento|incontro|colloquio|lezione|conferenza|esame|udienza)'
TIME_ONLY=r'\b(?:oggi|domani|ieri|venerdì|lunedì|martedì|mercoledì|giovedì|sabato|domenica|mattina|pomeriggio|sera|ore|alle|entro|pausa pranzo|fine settimana)\b'
HYPOTHESIS=r'\b(?:se\s+\w+(?:assi|essi|issi|asse|esse)|qualora|nell[’\']ipotesi|se\s+mai)\b'
NEGATION=r'\b(?:non\s+(?:devo|deve|dobbiamo|voglio|intendevo|fare|chiamare|scrivere|prenotare|mandare)|evitare\s+di|annullare\s+la\s+richiesta)\b'
COMPLETED=r'\b(?:ho\s+(?:già\s+)?(?:fatto|restituito|inviato|mandato|chiamato|prenotato|consegnato|pagato|finito|completato)|(?:è|sono)\s+(?:già\s+)?(?:stato|stata|stati|state)\s+(?:fatto|fatta|completato|completata))\b'
ATTR_ONLY=r'^(?:è\s+(?:già\s+)?fissat[aoie]\b|se\s+riesco\b|(?:alle|entro|durante|per|nel)\s+(?:la\s+|il\s+|le\s+|i\s+)?)'
REPORTING=r'\b(?:coinvolge|riguarda|contiene|costa|significa)\b'
IDEA=r'\b(?:sarebbe\s+interessante|mi\s+piacerebbe)\b'
QUOTES='«»“”"'

def _has(p,s):return bool(re.search(p,s,re.I))
def clause(note, quote):
    pos=note.find(quote)
    if pos<0:return note,False
    # split at sentence delimiters and explicit contrastive punctuation;
    # not commas, which may carry qualifiers and alternatives.
    start=max(note.rfind('.',0,pos),note.rfind(';',0,pos),note.rfind('!',0,pos),note.rfind('?',0,pos))+1
    ends=[j for ch in '.;!?' if (j:=note.find(ch,pos+len(quote)))>=0]
    end=min(ends) if ends else len(note)
    return note[start:end].strip(), True

def quoted_instruction(note,quote):
    pos=note.find(quote)
    if pos<0:return False
    before=note[:pos]
    for a,b in [('«','»'),('“','”'),('"','"')]:
        if before.count(a)>before.count(b):return True
    return False

def analyze(rec):
    q=rec['citazione'].strip(); note=rec['note_originale']; kind=rec['tipo_predetto']; intent=rec['intenzione_predetta']; action=rec['decisione_sandbox']
    context,found=clause(note,q)
    hard=[]; diagnostics=[]; score=0
    if not found:hard.append('QUOTE_NOT_IN_ORIGINAL')
    if action not in ('PROPOSE','CLARIFY'):hard.append('NOT_ACTIONABLE_BASELINE')
    if _has(r'^(?:se riesco|venerdì|lunedì|martedì|mercoledì|giovedì|sabato|domenica)\s*$',q):hard.append('STANDALONE_QUALIFIER')
    if _has(r'^è\s+fissat[aoie]\b',q):hard.append('STANDALONE_EVENT_ATTRIBUTE')
    if _has(r'^durante\s+la\s+pausa\b',q) or (_has(TIME_ONLY,q) and not _has(ACTION_WORDS+'|'+EVENT_WORDS,q)):
        hard.append('TEMPORAL_ONLY')
    if _has(REPORTING,q) and not _has(ACTION_WORDS,q):hard.append('INFORMATIONAL_STATEMENT')
    # A quoted instruction is not an instruction to the assistant.
    if quoted_instruction(note,q):hard.append('QUOTED_CONTENT')
    if _has(HYPOTHESIS,context):hard.append('HYPOTHETICAL_CONTEXT')
    if _has(NEGATION,context):
        # If an explicit contrastive "invece" makes the quote a separate positive clause,
        # don't blindly block an action appearing after it.
        cut=re.search(r'\b(?:invece|ma\s+devo)\b',context,re.I)
        if not (cut and q in context[cut.start():]):hard.append('NEGATED_CONTEXT')
    if _has(COMPLETED,context) and intent=='COMMITTED':
        if not _has(r'\b(?:domani|devo|dovrò)\b',q):hard.append('COMPLETED_CONTEXT')
    if _has(IDEA,context) and intent=='TENTATIVE':hard.append('UNDECIDED_IDEA')
    if kind=='EVENT' and _has(r'^(?:avvisare|imballare|ritirare|mandare|controllare|scrivere|inviare|prenotare|chiamare)\b',q):hard.append('EVENT_TASK_TYPE_CONFLICT')
    # Identify missing alternative in a tentative meeting; don't propose an incomplete object.
    if intent=='TENTATIVE' and _has(r'\b(?:o|oppure)\s+[A-ZÀ-Ú][a-zà-ú]+\b',context) and not _has(r'\b(?:o|oppure)\s+[A-ZÀ-Ú][a-zà-ú]+\b',q):hard.append('MISSING_ALTERNATIVE')
    if _has(ACTION_WORDS,q):score+=5; diagnostics.append('ACTION_CUE')
    if _has(EVENT_WORDS,q):score+=4;diagnostics.append('EVENT_ENTITY')
    if _has(r'\b(?:devo|deve|vorrei|potrei|ricordarmi|dovrei)\b',q):score+=3;diagnostics.append('INTENT_EXPLICIT')
    if _has(r'\b(?:domani|entro|venerdì|mercoledì|giovedì|martedì|ore|alle)\b',q):score+=1
    if kind=='TASK' and _has(ACTION_WORDS,q):score+=2
    if kind=='EVENT' and _has(EVENT_WORDS,q):score+=2
    if len(q.split())<3:score-=3
    if action=='PROPOSE':score+=1
    return {'review_id':rec['review_id'],'scenario_id':rec['scenario_id'],'candidate_id':rec['candidate_id'], 'text':q,'kind':kind,'intent':intent,'decision':action,'old_popup':rec['popup_mostrato']=='1','context':context, 'score':score,'reject_reasons':sorted(set(hard)), 'diagnostics':diagnostics, 'eligible':not hard}

def run(records):
    evaluated=[analyze(r) for r in records]
    bynote=collections.defaultdict(list)
    for v in evaluated:bynote[v['scenario_id']].append(v)
    selected={}
    for sid,vs in bynote.items():
        viable=[v for v in vs if v['eligible']]
        selected[sid]=sorted(viable,key=lambda x:(-x['score'],x['candidate_id']))[0]['review_id'] if viable else None
    for v in evaluated:v['new_popup']=v['review_id']==selected[v['scenario_id']]
    return evaluated,selected

def write(output,records):
    output.mkdir(exist_ok=True,parents=True)
    values,selected=run(records)
    with (output/'candidate_diagnostics.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['review_id','scenario_id','candidate_id','text','kind','intent','decision','old_popup','new_popup','eligible','score','context','reject_reasons','diagnostics']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{**v,'reject_reasons':'|'.join(v['reject_reasons']),'diagnostics':'|'.join(v['diagnostics'])} for v in values])
    with (output/'selection_by_note.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['scenario_id','old_popup_id','new_popup_id','outcome'])
        for sid in sorted(selected):
            prev=next((v['review_id'] for v in values if v['scenario_id']==sid and v['old_popup']),None)
            new=selected[sid]; w.writerow([sid,prev or '',new or '', 'UNCHANGED' if prev==new else ('SUPPRESSED' if not new else 'REPLACED' if prev else 'NEW')])
    return values,selected

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input',default=str(ROOT/'data'/'review_21.csv'));a.add_argument('--out',default=str(ROOT/'results'))
    args=a.parse_args()
    with open(args.input,encoding='utf-8-sig') as f:records=list(csv.DictReader(f))
    values,sel=write(pathlib.Path(args.out),records)
    print(json.dumps({'candidates':len(values),'notes':len(sel),'baseline_popups':sum(v['old_popup'] for v in values),'new_popups':sum(v['new_popup'] for v in values),'changed_notes':sum(any(v['old_popup']!=v['new_popup'] for v in values if v['scenario_id']==sid) for sid in sel),'rejected':sum(not v['eligible'] for v in values)},ensure_ascii=False,indent=2))
