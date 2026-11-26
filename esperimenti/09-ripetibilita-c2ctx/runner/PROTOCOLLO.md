# Protocollo — I1 vs I1-R (diagnostica interna)

- **Variabile controllata:** solo riferimenti contestuali I1 revisionati manualmente in 12 note, per 18 azioni. Azioni, citazioni, ID, note originali e dati temporali invariati; prompt e schema di C2-CTX v01 invariati.
- **Materiali congelati:** `estrazioni_x2_congelate.json`, `note_test40_DIAGNOSTICO.json`, `interfaccia_I1_ORIGINALE.json`, codice originale `prova_c2_ctx.py`, `prompt_C2_CTX.txt`, componenti freeze S2. Lo script controlla la ricostruzione identica di I1 dall'estrattore, insieme agli hash della pipeline congelata.
- **Input I1-R:** modifiche manuali documentate in `registro_correzioni.csv`, citazioni esatte e span calcolati in Python. Nessuna etichetta di classificazione inserita nell'input.
- **Output:** confronto appaiato per ciascuna delle 39 azioni, 78 inferenze; esiti JSON, chiamate, tempi, differenze negli attributi `kind`, `intent`, `subject_owner`, `polarity`, `completion`, `uncertain`.
- **Analisi primaria:** valutare le 18 azioni modificate. Le altre 21 sono controlli con input identico; eventuali differenze devono essere indagate come variabilità dell'esecuzione.
- **Limiti a monte:** in 008 `a2` è un frammento temporale improprio, in 021 `a2` è una non-decisione rappresentata come azione; 028 non contiene l'azione negata. Queste anomalie sono conservate, non sanate. `relations` restano vuote e non si attribuisce un nesso causale ai soli metadati.
- **Validazione:** confronto diagnostico su dati già conosciuti; le correzioni manuali sono un intervento assistito. Nessuna valutazione end-to-end dei popup, nessuna validazione indipendente, nessuna adozione automatica.
- **Decisione:** mantenere `X0+C2+Z+S2-V` come configurazione candidata finché un nuovo protocollo e dataset indipendente non sosterranno una modifica.
