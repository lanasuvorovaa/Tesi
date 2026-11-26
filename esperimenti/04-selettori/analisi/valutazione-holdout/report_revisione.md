# Revisione holdout UC-01 — 21 novembre 2026

## Natura della verifica
32 note sintetiche nuove rispetto al development set, 53 frammenti X0, confronto appaiato baseline X0+C0+Z+S0 e candidata X0+C2+Z+S1. Il file gold è marcato BOZZA_DA_CONFERMARE e i tre casi temporali sono DA_VALUTARE; i giudizi qui sotto sono una revisione interpretativa, non un gold indipendente approvato. Dataset sintetico, non test su note reali.

## Conteggi osservati
- Popup baseline: 13; candidata: 13; note con selezione diversa: 6.
- Valutazione per nota (A = pienamente appropriata, P = parziale, E = errata/mancante, U = incerta secondo policy): baseline {'P': 5, 'A': 18, 'E': 7, 'U': 2}; candidata {'P': 6, 'A': 18, 'E': 6, 'U': 2}.
- Casi 030–032 non entrano in un confronto definitivo di accuratezza senza arbitrare le regole sulle date vaghe, sugli eventi non confermati e sulle intenzioni condizionate.

## Differenze sostanziali
- 004 REGRESSIONE: baseline propone invio scansione; candidata seleziona una constatazione sul commercialista.
- 006 MIGLIORAMENTO PARZIALE: candidata recupera la lezione; mancano dettagli temporali nel popup.
- 019 MIGLIORAMENTO: candidata evita «Lo riporto per il verbale».
- 021 REGRESSIONE: candidata propone un'aspirazione vaga («Forse un giorno...»).
- 023 MIGLIORAMENTO: candidata evita un frammento di decisione privo di azione autonoma.
- 028 DIFFERENZA NEUTRA: entrambe selezionano una delle tre attività valide.

## Limiti comuni prioritari
- 007, 009: EVENT/COMMITTED e PROPOSE per entrambe, ma nessun popup; indagare filtro/criteri di selezione.
- 016: X0 non estrae il ticket da inviare dopo la negazione della chiamata; né C2 né S1 possono recuperarlo.
- 001, 006, 008: frammentazione separa azione/evento e riferimenti temporali; una proposta può essere valida ma incompleta.
- 003, 027, 028: vincolo della singola proposta lascia attività aggiuntive fuori dall'output.
- 030: promemoria non proposto, ma policy di gestione data vaga da definire prima del giudizio definitivo.

## Decisione
La candidata è promettente ma NON è ancora dimostrata superiore in modo conclusivo: due regressioni su 004 e 021, carenze comuni su eventi e azioni non estratte. Conservare entrambe le configurazioni congelate e gli hash; non modificare i prompt sulla base dell'holdout prima di registrare questi risultati come validazione. Per sviluppi successivi, usare un nuovo set e protocollo rinnovato.

## Nota metodologica
Le annotazioni per 53 frammenti originali sono mantenute in allegato senza compilare un gold per-frammento ex post. La revisione dettagliata completata riguarda i 32 output per nota. Per una metrica di classificazione sui frammenti occorre concordare un gold indipendente e criteri TASK/EVENT/FACT e intention, poi effettuare l'annotazione separatamente.
