# Esperimento X0/X1 – correzione v02

La prima esecuzione X1 è stata bloccata dal vincolo del trasporto `constrained_api.build_request`, che accetta solo il prompt X0 registrato. Nessuna delle 40 note X1 ha prodotto inferenza valida. **Non interpretare quei risultati come accuratezza X1.**

Questa versione lascia invariati i file congelati e il testo dei prompt. L’adattatore sperimentale `request_x1` costruisce la richiesta tramite la funzione originale con lo schema di estrazione `atomic_quotes` e sostituisce esclusivamente il contenuto del messaggio system con il prompt X1. Temperatura, seed, JSON Schema e chiamata HTTP restano identici.

## Esecuzione Mac

1. Estrai questa cartella sul Desktop (non sovrascrivere la versione precedente).
2. Apri il Terminale ed esegui:

```bash
cd "$HOME/Desktop/esperimento_x1_completezza_uc01_v02_CORRETTO"
python3 test_x1.py
bash esegui_diagnostico.command
```

3. Comprimi e invia la nuova cartella `risultati/x0_vs_x1_...`, contenente `confronto_estrazioni.csv`, `confronto_candidati.csv`, `manifest.json`, `report.md` e `dettagli/`.

Prima di valutare la qualità assicurarsi che siano presenti **40 righe X1 senza errori di protocollo**. È normale che possano esistere errori di estrazione/validazione specifici delle note; registrarli separatamente.

Il set di 40 note è già conosciuto e resta diagnostico, non una validazione indipendente.
