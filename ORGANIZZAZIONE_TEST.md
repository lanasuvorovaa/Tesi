# Come organizzare i test

Per facilitare la consultazione da parte del relatore, consiglio di non caricare subito tutti gli ZIP accumulati. Preparare prima una cartella per ciascun esperimento, includendo:

1. `README.md` — cosa si voleva verificare, cosa è cambiato e risultato principale;
2. `protocollo.md` — dataset, modello, parametri e condizioni del confronto;
3. `codice/` — script per ripetere il test, senza percorsi personali o dipendenze non dichiarate;
4. `risultati/` — CSV/JSON riassuntivi, eventualmente output completi anonimizzati;
5. `manifest.json` — hash e versioni, se presenti.

Ordine proposto dei gruppi:

- `01_primi_test_e_pipeline/`
- `02_confronto_modelli/`
- `03_classificazione_C/`
- `04_selettore_S/`
- `05_estrazione_X/`
- `06_proiezione_contesto_P0_P1/`
- `07_interfaccia_I1_e_C2_CTX/`
- `08_audit_I1_e_I1_R/`
- `09_ripetibilita_C2_CTX/`

Questi sono nomi proposti e non attestano che i file siano già stati spostati o pubblicati. Evitare di confondere la data di esecuzione con la data di pubblicazione sul repository.

**Da non pubblicare senza controllo:** log grezzi, note personali, credenziali, percorsi utente, dataset non autorizzati, modelli scaricati con licenze che non ne consentano la redistribuzione. Per i modelli, è preferibile conservare il nome e l'hash e rimandare alla fonte ufficiale, senza caricare il GGUF.
