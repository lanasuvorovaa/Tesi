# Revisione diagnostica I1 originale vs I1-R — UC-01

## Protocollo e tracciabilità
Confronto appaiato di 39 azioni estratte e validate da X2 su 40 note sintetiche già note; 78 classificazioni formalmente valide. I1-R modifica il contesto per 18 azioni su 12 note. C2-CTX v01 e modello dichiarati congelati dal manifest; Z e S2-V non eseguiti. Interpretazione diagnostica e **non** validazione indipendente né confronto end-to-end sui popup.

## Risultati
- 35 azioni con le sei uscite (`kind`, `intent`, `subject_owner`, `polarity`, `completion`, `uncertain`) identiche.
- 4 azioni con almeno una uscita cambiata (011-a1, 026-a1, 028-a1, 039-a1).
- Nessun cambiamento su `kind` o `subject_owner`: TASK 38 / EVENT 1 e SELF 39 / 39 in entrambe le condizioni.
- Caso 011-a1: input dei contesti identico, ma `completion` cambia PENDING → DONE e `uncertain` True → False. Questo cambiamento **non** si può attribuire alla revisione dell'interfaccia: richiede valutazione della ripetibilità.
- Caso 026-a1: `intent` COMMITTED → COMPLETED per «Ho disdetto la visita»; miglioramento plausibile.
- Caso 028-a1: `completion` DONE → PENDING è un recupero, ma `intent` COMMITTED → TENTATIVE è un peggioramento; `polarity` resta NEGATIVE nonostante «devo scaricare il QR code» sia l'azione positiva. Non è una correzione completa.
- Caso 039-a1: `intent` COMMITTED → TENTATIVE, `polarity` POSITIVE → UNCLEAR e `completion` DONE → PENDING. Diminuisce l'assertività su un imperativo *citato*, ma la classificazione rimane TASK e SELF; l'altra azione citata (039-a2) rimane invariata.

## Errori persistenti evidenti
- Eventi 008-a1/a2 e 034-a1 restano TASK; il riconoscimento EVENT non migliora.
- Terzi 017-a1 e 025-a1 restano SELF anche dopo il contesto rettificato.
- Desiderio 020-a1 resta COMMITTED nonostante «Mi piacerebbe» sia marcato modality.
- 021-a1/a2 restano TASK/TENTATIVE: non si risolve automaticamente l'assenza di decisione.
- Citazione del romanzo 038-a1 rimane TASK/COMMITTED/SELF/DONE; 039-a2 rimane TASK/COMMITTED/SELF/DONE.
- 028-a1 rimane NEGATIVE: la negazione della prima azione viene erroneamente estesa alla seconda.

## Conclusione
I1-R migliora diversi ruoli e portate del contesto, ma non risolve i limiti cruciali di C2-CTX v01. Non adottare il classificatore contestuale; conservare la candidata X0+C2+Z+S2-V. Prima di progettare C2-CTX v02, testare ripetibilità su input invariati e definire casi unitari di controllo per EVENT/TASK, SELF/OTHER, citazione, negazione e desiderio. Non attribuire a I1-R cambiamenti non sostenuti da un input differente. Una futura valutazione indipendente dovrà utilizzare nuove note.
