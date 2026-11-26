#!/usr/bin/env python3
"""S1 = S0 frozen + extra deterministic semantic-autonomy veto; no gold or note IDs."""
import re
from replay_24 import choose as frozen_choose

# Generic conditions only: never look at dataset IDs, gold labels, or expected popup.
CONNECTIVE_FRAGMENT = re.compile(r"^\s*(?:o|oppure|ovvero|cioè|che|ma)\s+",re.I)
DECISION_STATUS = re.compile(r"\b(?:devo|dobbiamo|dovrei)\s+(?:ancora\s+)?(?:decidere|valutare|scegliere)\b",re.I)
NO_COMMITMENT = re.compile(r"\b(?:non\s+(?:ho|abbiamo)\s+(?:ancora\s+)?deciso|non\s+so\s+ancora|sto\s+valutando\s+se)\b",re.I)


def autonomy_reasons(row):
    q=row['citazione'].strip()
    reasons=[]
    if CONNECTIVE_FRAGMENT.search(q):
        reasons.append('S1_DANGLING_CONNECTOR')
    # Meta-decision about whether to act is not itself a concrete action;
    # qualifiers are evaluated on the text and not on the person's name.
    if DECISION_STATUS.search(q):
        reasons.append('S1_META_DECISION')
    if NO_COMMITMENT.search(q) and not re.search(r'\b(?:inviare|mandare|chiamare|scrivere|controllare|prenotare)\b',q,re.I):
        reasons.append('S1_UNDECIDED_STATE')
    return reasons


def choose_s1(records):
    baseline, old_selected = frozen_choose(records)
    augmented=[]
    for r,diag in zip(records,baseline):
        d=dict(diag)
        extra=autonomy_reasons(r)
        d['s1_veto_reasons']=extra
        d['reject_reasons']=sorted(set(d['reject_reasons']+extra))
        d['eligible']=bool(d['eligible'] and not extra)
        augmented.append(d)
    eligible=[d for d in augmented if d['eligible']]
    selected=sorted(eligible,key=lambda d:(-d['score'],d['candidate_id']))[0] if eligible else None
    for d in augmented:
        d['new_popup']=bool(selected and d['candidate_id']==selected['candidate_id'])
    return augmented, selected
