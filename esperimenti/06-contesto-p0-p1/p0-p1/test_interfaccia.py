import unittest
from proiezione_contesto import project
from prova_interfaccia import load_sources,ROOT

class TestProjection(unittest.TestCase):
 def test_full_deadline(self):
  note='Devo spedire il campione al laboratorio entro lunedì mattina.'
  a=[{'id':'a1','action_quote':'spedire','action_span':[5,12],'context':[]}]
  self.assertEqual(project(note,a,'P1_CLAUSOLA')[0]['quote'],note.rstrip('.'))
 def test_two_actions_separate(self):
  note='Domani devo pagare il bollo e inviare la ricevuta alla contabilità.'
  a=[{'id':w,'action_quote':w,'action_span':[note.index(w),note.index(w)+len(w)],'context':[]} for w in ('pagare','inviare')]
  out=project(note,a,'P1_CLAUSOLA')
  self.assertEqual(len(out),2)
  self.assertNotIn('inviare',out[0]['quote'])
  self.assertNotIn('pagare',out[1]['quote'])
 def test_negation_separated(self):
  note='Non devo stampare i biglietti, ma domani devo scaricare il QR code.'
  s=note.index('scaricare')
  a=[{'id':'a1','action_quote':'scaricare','action_span':[s,s+len('scaricare')],'context':[]}]
  out=project(note,a,'P1_CLAUSOLA')[0]['quote']
  self.assertNotIn('Non devo stampare',out)
  self.assertIn('scaricare il QR code',out)
 def test_no_fabrication(self):
  cases,_=load_sources(ROOT/'note_test40_DIAGNOSTICO.json',ROOT/'estrazioni_x2_congelate.json')
  self.assertEqual(len(cases),40)
 def test_reuse_and_exactness(self):
  cases,sources=load_sources(ROOT/'note_test40_DIAGNOSTICO.json',ROOT/'estrazioni_x2_congelate.json')
  for case in cases:
   for variant in ('P0_ATOMICA','P1_CLAUSOLA'):
    for p in project(case['nota'],sources[case['id']]['accepted'],variant):
     self.assertIn(p['quote'],case['nota'])
     self.assertIn(p['atomic'],p['quote'])

if __name__=='__main__':unittest.main()
