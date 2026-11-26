#!/usr/bin/env python3
"""Varianti isolate di S1. Nessun gold/ID di nota o nuova inferenza.

S2-V: veto aggiuntivi sulla proposizione citata. S2-R: solo punteggio.
S2-VR: entrambe. S1 immutato e chiamato come riferimento.
"""
import re
from selettore_s1 import choose_s1

# Regole generiche italiane, prudenziali e deliberatamente limitate.
# Evitare di interpretare da soli il contenuto della nota: valutare la citazione.
ASPIRATION = re.compile(r"\b(?:forse\s+(?:un\s+giorno|prima\s+o\s+poi)|magari\s+un\s+giorno|un\s+giorno\s+(?:mi\s+piacerebbe|vorrei)|sogno\s+di|mi\s+piacerebbe\s+un\s+giorno)\b",re.I)
PRESENT_DESCRIPTION = re.compile(r"^\s*(?:l[’']|il\s+|la\s+|lo\s+|i\s+|gli\s+|le\s+|un\s+|una\s+)(?:[\wÀ-ÿ’'-]+\s+){0,5}(?:aspetta|attende|contiene|prevede|riguarda|costa|coinvolge|risulta|indica|descrive|comprende|richiede)\b",re.I)
# First-person explicit action or an infinitive used as an instruction in a list.
FIRST_PERSON_ACTION = re.compile(r"\b(?:(?:devo|dobbiamo|voglio|intendo|ho\s+da)\s+(?:ancora\s+)?(?:\w+)|(?:gli|le|ti|vi|lo|la|li|ne)\s+(?:mando|invio|scrivo|porto|consegno|spedisco|telefono)|(?:mando|invio|scrivo|porto|consegno|spedisco|controllo|verifico|preparo|prenoto)\b)",re.I)
INFINITIVE_TASK = re.compile(r"^\s*(?:contattare|stampare|controllare|verificare|preparare|inviare|mandare|scrivere|organizzare|imballare|ritirare|avvisare|consegnare|prenotare|spedire|pagare|aggiornare|chiamare)\b",re.I)


def veto_reasons(record):
    quote=record['citazione'].strip()
    kind=record['tipo_predetto']
    reasons=[]
    if kind=='TASK' and ASPIRATION.search(quote):
        reasons.append('S2_V_ASPIRATION_NO_ACTION')
    if kind=='TASK' and PRESENT_DESCRIPTION.search(quote) and not FIRST_PERSON_ACTION.search(quote):
        reasons.append('S2_V_DESCRIPTIVE_CLAUSE')
    return reasons


def ranking_delta(record):
    """Only modify preference, never eligibility. Distinct from V."""
    q=record['citazione'].strip(); kind=record['tipo_predetto']
    delta=0; tags=[]
    if kind=='TASK' and (FIRST_PERSON_ACTION.search(q) or INFINITIVE_TASK.search(q)):
        delta+=4; tags.append('S2_R_EXPLICIT_ACTION')
    if kind=='TASK' and PRESENT_DESCRIPTION.search(q):
        delta-=5;tags.append('S2_R_DESCRIPTIVE')
    if kind=='TASK' and ASPIRATION.search(q):
        delta-=3;tags.append('S2_R_ASPIRATION')
    return delta,tags


def choose_variant(records,variant='S1'):
    if variant not in ('S1','S2-V','S2-R','S2-VR'):
        raise ValueError('Variante non riconosciuta: '+variant)
    diags, _=choose_s1(records)
    updated=[]
    for rec,d in zip(records,diags):
        d=dict(d)
        extra=veto_reasons(rec) if variant in ('S2-V','S2-VR') else []
        delta,tags=ranking_delta(rec) if variant in ('S2-R','S2-VR') else (0,[])
        d['s2_veto_reasons']=extra
        d['s2_ranking_reasons']=tags
        d['s2_ranking_delta']=delta
        d['score']=d['score']+delta
        d['reject_reasons']=sorted(set(d['reject_reasons']+extra))
        d['eligible']=bool(d['eligible'] and not extra)
        updated.append(d)
    valid=[d for d in updated if d['eligible']]
    chosen=sorted(valid,key=lambda d:(-d['score'],d['candidate_id']))[0] if valid else None
    for d in updated:
        d['new_popup']=bool(chosen and d['candidate_id']==chosen['candidate_id'])
    return updated,chosen
