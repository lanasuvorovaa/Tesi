# UC-01 — Ripetibilità di C2-CTX v01

Si ripete **lo stesso input I1-R** tre volte per azione, senza modificare il prompt, il modello o gli attributi di inferenza. Non è un test di accuratezza.

## Selezione (20 azioni)

- Tutte le **18 azioni** i cui contesti erano stati revisionati nel precedente esperimento I1-R.
- Due controlli invariati: `UC01-S2TEST-011/a1` (dove si è già osservata una discrepanza nonostante lo stesso input) e `UC01-S2TEST-002/a1`.
- Tre round, in ordine diretto/inverso/diretto: **60 inferenze**; stessa richiesta testuale per azione in tutti i round. Vengono registrati gli hash degli input e i JSON grezzi.

## Sul Mac

Estrarre `esperimento_ripetibilita_c2ctx_uc01_v01` sul Desktop, mantenendo la cartella e il runtime originali come per I1-R. Eseguire:

```bash
cd "$HOME/Desktop/esperimento_ripetibilita_c2ctx_uc01_v01"
python3 test_ripetibilita.py
bash esegui_ripetibilita.command
```

**Nota:** il comando bash esegue già i test: è sufficiente eseguire `bash esegui_ripetibilita.command` da solo. Non ripete automaticamente l'audit offline e non crea due cartelle con lo stesso nome. Il runner genera un identificativo con microsecondi.

Caricare lo ZIP della nuova cartella `risultati/ripetibilita_...`.

## Altre opzioni

`python3 prova_ripetibilita.py --offline-only` per audit senza inferenza. `--scope all` per tutte le 39 azioni. `--repeats 5` per cinque ripetizioni. Non cambiare queste opzioni nel primo confronto.

## Lettura del risultato

`sintesi_per_azione.csv` misura l'identità esatta della sestupla `kind, intent, subject_owner, polarity, completion, uncertain`; `ripetizioni.csv` contiene tutti gli output. La presenza di differenze su input e parametri identici indica instabilità della risposta. La stabilità, da sola, non garantisce correttezza.

Le note sono sintetiche e già utilizzate nello sviluppo. Nessuna modifica a C2-CTX v01, Z, S2-V o alla configurazione candidata `X0+C2+Z+S2-V`.
