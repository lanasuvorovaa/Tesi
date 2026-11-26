# Valutazione diagnostica X0 vs X1 — UC-01

**Data:** 2026-11-23. **Campione:** 40 note sintetiche già utilizzate nello sviluppo dei selettori. **Confronto:** X0+C2+Z+S2-V vs X1+C2+Z+S2-V. Solo il prompt di estrazione cambia. Risultati di sviluppo, non test indipendente di X1.

## Integrità e risultati quantitativi

- Entrambe le varianti completano 40 note; 80 righe nel confronto estrazioni.
- Frammenti validati: X0 55, X1 37. Non interpretare questo come minor recall, poiché X1 accorpa più informazioni in ciascun frammento.
- Popup: X0 21, X1 18. Testi popup differenti in 10 note (001, 006, 021, 024, 030, 031, 032, 033, 035, 037). Nel 024 la differenza è soltanto punteggiatura e non semantica.
- Chiamate al modello: X0 95, X1 77 (media 2,375 e 1,925 per nota).
- Tempo logico: X0 125.946,8 ms totali (3,149 s/nota); X1 98.236,9 ms (2,456 s/nota). Differenza su questo ambiente, non benchmark generalizzabile.

## Revisione qualitativa proposta

| Esito | X0 | X1 |
|---|---:|---:|
| A | 24 | 25 |
| P | 7 | 5 |
| E | 9 | 10 |

Legenda: A = proposta appropriata e autonoma o assenza corretta; P = proposta utile ma incompleta / non atomica; E = proposta errata oppure omissione di un'opportunità. Si tratta di **annotazione assistita, da verificare** prima di usare cifre in tesi. Nel caso 029 si applica la policy decisa **dopo** il test: l'obbligo impersonale di controllare il caricatore è proponibile.

## Conclusioni per caso

- Miglioramenti netti: 001 e 006 (scadenze/luoghi), 021 (niente falso popup). X1 valida anche citazioni in 005 e 022 che X0 rifiutava, ma questo non produce un miglioramento del popup.
- Peggioramenti netti: 033 (sparisce il task), 035 (citazione invalidata e task perso). Il caso 030 passa da un task individuale valido a un popup che unisce tre attività; è più completo come testo ma meno corretto come unità operativa.
- Casi misti: 031 e 032 ricostruiscono più contesto ma fondono due task; 037 conserva il contesto ma ingloba materiale descrittivo.
- Problemi immutati: 004 e 011 (mancati popup), 013 e 014 (azioni di terzi), 024 (intenzione vaga), 028 e 029 (attività positive escluse), 036 (anafora).

## Decisione

**Non sostituire X0 con X1.** X1 dimostra un miglioramento nella conservazione delle informazioni, ma la segmentazione più ampia causa perdita di attività e proposte che contengono molteplici azioni. Mantenere X0+C2+Z+S2-V come candidata e X1 come variante diagnostica. Progettare in un futuro esperimento un'estrazione con *unità di azione atomiche* corredate di contesto, senza unire più obblighi in un'unica citazione, e verificarla su note nuove non viste. Eventuali metriche finali vanno validate da revisione manuale indipendente.

## Nota sul validatore

X1 migliora la fedeltà letterale in 005 e 022, ma fallisce in 035. Allungare le citazioni non risolve automaticamente la compatibilità con la validazione delle evidenze.
