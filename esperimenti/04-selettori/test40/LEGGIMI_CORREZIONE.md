# Correzione tecnica v02 — test UC-01 S2 (40 note)

La prima esecuzione non ha prodotto inferenze: tutte le 40 note sono state respinte con l’errore «La data di riferimento deve avere un fuso orario».

**Unica modifica al dataset**: in tutti i record `reference_datetime` passa da `2026-12-03T10:00:00` a `2026-12-03T10:00:00+01:00` (Europe/Rome a dicembre). Nessuna nota, ID, annotazione gold o codice del selettore è modificato. La correzione è documentata nel nuovo manifest e il vecchio hash è conservato per tracciabilità.

## Come usare il pacchetto

1. Estrarre lo ZIP sul Desktop. NON modificare `selettore_s2_uc01_v01`.
2. Mantenere sul Desktop anche `selettore_s2_uc01_v01`, il modello e il runtime usati finora.
3. Da Terminale:

```bash
cd "$HOME/Desktop/testset_s2_40_uc01_CORRETTO_v02"
python3 verifica_dataset.py
bash esegui_test40.command
```

**Nota:** lo script di lancio usa `selettore_s2_uc01_v01` già sul Desktop. Il gold resta escluso dagli input al modello. Invia lo ZIP della cartella `selettore_s2_uc01_v01/risultati/nuove_note_...` una volta conclusa l’esecuzione.

Il test rimane un holdout sintetico. La correzione tecnica del fuso è stata necessaria prima di ottenere predizioni, quindi non nasce dall’osservazione dei risultati dei selettori.
