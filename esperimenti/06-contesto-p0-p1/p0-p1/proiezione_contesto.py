"""Deterministic, conservative contiguous projection of validated X2 actions.

P0: original atomic quote. P1: contiguous source-text clause around the action,
segmented by punctuation, adversative markers, and other accepted action spans.
Never concatenate separate spans, infer words, or repair X2 citations.
"""
import re

BOUNDARY = re.compile(r'[;.!?\n]|,\s*(?=ma\b|per[oò]\b|invece\b)', re.I)
JOIN = re.compile(r'\s+(?:e|poi|quindi)\s+', re.I)

def project(note, accepted, mode):
    if mode not in ('P0_ATOMICA','P1_CLAUSOLA'):
        raise ValueError('Unknown projection')
    result=[]
    accepted=sorted(accepted,key=lambda x:x['action_span'][0])
    for idx, action in enumerate(accepted):
        start,end=action['action_span']
        assert note[start:end]==action['action_quote'], 'Source-text offset mismatch'
        if mode=='P0_ATOMICA':
            quote=action['action_quote']; reasons=['ACTION_ONLY']
        else:
            left=0;right=len(note);reasons=[]
            for m in BOUNDARY.finditer(note):
                if m.end()<=start:left=m.end()
                elif m.start()>=end:
                    right=m.start();break
            if idx>0:
                prev_end=accepted[idx-1]['action_span'][1]
                if prev_end<start and prev_end>=left:
                    between=note[prev_end:start]
                    joins=list(JOIN.finditer(between))
                    if joins:
                        left=max(left,prev_end+joins[-1].end());reasons.append('SEPARATED_PREVIOUS_ACTION')
                    else:
                        left=max(left,prev_end);reasons.append('BOUND_PREVIOUS_ACTION')
            if idx<len(accepted)-1:
                next_start=accepted[idx+1]['action_span'][0]
                if end<next_start and next_start<=right:
                    between=note[end:next_start]
                    joins=list(JOIN.finditer(between))
                    if joins:
                        right=min(right,end+joins[0].start());reasons.append('SEPARATED_NEXT_ACTION')
                    else:
                        right=min(right,next_start);reasons.append('BOUND_NEXT_ACTION')
            left=max(0,min(left,start));right=min(len(note),max(right,end))
            quote=note[left:right].strip(' \t\r\n,;:.!?')
            # Remove dangling adversative connector left behind by clause splitting.
            quote=re.sub(r'^(?:ma|però|invece)\s+', '', quote, flags=re.I)
            if not quote or note.find(quote)<0 or action['action_quote'] not in quote:
                quote=action['action_quote'];reasons.append('FALLBACK_ATOMIC')
            else:reasons.append('EXACT_CONTIGUOUS_CLAUSE')
        result.append({'id':action['id'],'quote':quote,'atomic':action['action_quote'],
                       'context':action.get('context',[]),'reasons':reasons})
    # stage1 rejects duplicate quote; dedup only identity duplicates, record reduced cardinality.
    unique=[];seen=set()
    for item in result:
        if item['quote'] in seen:item['reasons'].append('DUPLICATE_COLLAPSED');continue
        seen.add(item['quote']);unique.append(item)
    return unique
