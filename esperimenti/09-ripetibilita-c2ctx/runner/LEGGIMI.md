# UC-01 — Confronto I1 originale vs I1-R v01

## Obiettivo
Confrontare, a classificatore C2-CTX v01 identico, i 39 input già estratti da X2 v02 con i contesti originari (I1) e i contesti revisionati manualmente (I1-R). **Non** cambia nessuna azione, nessun prompt, modello, Z o selettore; Z e S non vengono eseguiti.

## Requisiti
Mac con lo stesso modello Qwen3-1.7B GGUF e `~/Desktop/confronto_slm_uc01_v01` dell'esperimento precedente. Non è necessario sostituire il pacchetto precedente.

## Esecuzione
1. Estrarre l'archivio `esperimento_i1r_uc01_v01.zip` sul Desktop.
2. Nel Terminale:

```bash
cd "$HOME/Desktop/esperimento_i1r_uc01_v01"
python3 test_i1r.py
bash esegui_test.command
```

`esegui_test.command` ripete i test prima del runner, ed esegue **solo il runner di inferenza** (non l'audit offline); non crea cartelle in conflitto. Se preferisci evitare di ripetere i test: `python3 prova_i1r.py`.

Il runner chiama 78 volte C2-CTX v01, generando output sotto `risultati/i1_vs_i1r_...`. Invia lo ZIP dell'intera cartella risultati, incluso `confronto_classificazioni.csv`, `report.json`, `manifest.json` e `dettagli`.

**Nota:** le correzioni I1-R sono annotazioni manuali preparate su note sintetiche già note. Non equivalgono a una validazione indipendente; si valutano le differenze di classificazione senza attribuire al sistema una capacità automatica di correggere i dati.
