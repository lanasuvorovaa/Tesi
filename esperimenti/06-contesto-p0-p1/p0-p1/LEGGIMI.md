# Esperimento interfaccia X2 → C2 — P0 vs P1

Questo pacchetto riutilizza le estrazioni X2 validate nell'esecuzione del 24 novembre 2026: **non ricalcola X2**. P0 passa l'azione atomica; P1 ricava una citazione più ampia e contigua dalla nota originale. C2, Z e S2-V sono copie congelate (hash controllati all'avvio).

## Sul Mac
Estrai la cartella `esperimento_interfaccia_x2_uc01_v01` sul Desktop. Mantieni la cartella preesistente `~/Desktop/confronto_slm_uc01_v01` e il modello GGUF come nelle precedenti prove.

Esegui dal Terminale:

```bash
cd "$HOME/Desktop/esperimento_interfaccia_x2_uc01_v01"
python3 test_interfaccia.py
bash esegui_diagnostico.command
```

**Facoltativo, senza modello:** `bash esegui_audit_offline.command` per verificare unicamente la costruzione delle citazioni.

Alla fine allega lo ZIP della cartella `risultati/proiezioni_...` che include `confronto_note.csv`, `confronto_candidati.csv`, `audit_proiezioni.csv`, `manifest.json`, `dettagli/`, `report.md` e, se presente, `llama_server.log`.

## Cosa aspettarsi
40 note × 2 varianti = 80 righe di confronto; il modello è chiamato soltanto per C2. L'esecuzione **non** esegue modifiche a calendari o note personali. Il report non assegna automaticamente giudizi A/P/E/U; questi richiedono revisione manuale.

## Fonte e limiti
`estrazioni_x2_congelate.json` proviene direttamente dai 40 file `dettagli/*_X2.json` dello ZIP `x0_x1_x2_20261124_233634.zip` conservato tra i materiali di origine. Non è necessario scaricare di nuovo quello ZIP. Lo studio è una prova **diagnostica su dati già conosciuti**, non una validazione indipendente.
