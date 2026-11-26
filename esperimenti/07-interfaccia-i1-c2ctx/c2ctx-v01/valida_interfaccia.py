#!/usr/bin/env python3
"""Validazione strutturale offline del contratto I1, senza inferenza.
Non certifica la corretta interpretazione semantica di scope/ruoli.
"""
import json
import sys
from pathlib import Path

ROLES = {'time','place','recipient','object','polarity','modality','condition','completion','speaker','discourse','antecedent'}
RELATIONS = {'before','after','depends_on','contrasts_with','same_event'}

def check_quote(text, item, path):
    quote, span = item.get('quote'), item.get('span')
    if not isinstance(quote, str) or not quote:
        raise ValueError(f'{path}: empty/invalid quote')
    if not isinstance(span,list) or len(span)!=2 or any(type(n) is not int for n in span):
        raise ValueError(f'{path}: invalid span')
    start,end=span
    if not 0<=start<end<=len(text) or text[start:end]!=quote:
        raise ValueError(f'{path}: quote/span mismatch')

def validate_document(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get('notes'),list):
        raise ValueError('missing notes[]')
    seen_notes=set()
    for ni,note in enumerate(doc['notes']):
        path=f'notes[{ni}]'
        text=note.get('text')
        if not isinstance(text,str) or not text.strip():
            raise ValueError(f'{path}: missing text')
        nid=note.get('note_id')
        if not isinstance(nid,str) or not nid or nid in seen_notes:
            raise ValueError(f'{path}: invalid/duplicate note_id')
        seen_notes.add(nid)
        actions=note.get('actions')
        if not isinstance(actions,list):
            raise ValueError(f'{path}: missing actions[]')
        ids=[a.get('id') for a in actions]
        if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
            raise ValueError(f'{path}: invalid/duplicate action ids')
        ids_set=set(ids)
        for ai,action in enumerate(actions):
            ap=f'{path}.actions[{ai}]'
            check_quote(text,action.get('action_evidence',{}),ap+'.action_evidence')
            contexts=action.get('context_refs',[])
            if not isinstance(contexts,list):
                raise ValueError(f'{ap}: invalid context_refs')
            for ci,context in enumerate(contexts):
                cp=f'{ap}.context_refs[{ci}]'
                check_quote(text,context,cp)
                if context.get('role') not in ROLES or context.get('source')!='explicit_text':
                    raise ValueError(f'{cp}: invalid role/source')
                scope=context.get('scope')
                if scope!='note_global' and (not isinstance(scope,list) or not scope or not set(scope)<=ids_set):
                    raise ValueError(f'{cp}: invalid scope')
                if context.get('confidence_policy')!='verified':
                    raise ValueError(f'{cp}: confidence_policy must be verified')
        for ri,relation in enumerate(note.get('relations',[])):
            rp=f'{path}.relations[{ri}]'
            if (relation.get('source_action_id') not in ids_set or
                relation.get('target_action_id') not in ids_set or
                relation.get('type') not in RELATIONS):
                raise ValueError(f'{rp}: invalid relation')
            check_quote(text,relation.get('evidence',{}),rp+'.evidence')
    return {'notes':len(doc['notes']), 'actions':sum(len(n['actions']) for n in doc['notes'])}

if __name__=='__main__':
    if len(sys.argv)!=2:
        sys.exit('Usage: python3 valida_interfaccia.py document.json')
    data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    result=validate_document(data)
    print('OK:',result)
