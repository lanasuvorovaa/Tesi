from selettore_s1 import choose_s1

def select_s1(case,result):
    records=[{'review_id':case['id']+'__'+c['id'],'scenario_id':case['id'],'candidate_id':c['id'],
              'note_originale':case['nota'],'citazione':c['evidence'],'tipo_predetto':c['kind'],
              'intenzione_predetta':c['intent'],'decisione_sandbox':c['sandbox_gate'],
              'popup_mostrato':'1' if c['selected'] else '0'} for c in result['candidates']]
    return choose_s1(records)
