# Validazione holdout UC-01 — v01

**Confronto:** baseline `X0+C0+Z+S0` vs candidata `X0+C2+Z+S1`.

Questo pacchetto contiene **32 nuove note sintetiche**, differenti dalle 24 di sviluppo. Non sono dati reali raccolti sul campo: i risultati misurano solo la generalizzazione a questo holdout sintetico. Nessun intervento ulteriore sui prompt/selettori prima della valutazione.

## Prima di eseguire

1. Estrarre il pacchetto sul Desktop, mantenendo il nome `validazione_holdout_uc01_v01`.
2. Conservare sul Desktop la cartella `confronto_slm_uc01_v01` con `.venv`, `runtime/llama.cpp/build/bin/llama-server` e il modello in `~/models/qwen3-1.7b-q4.gguf`.
3. **Prima di guardare i risultati**, confermare o correggere `gold_holdout32_PREDEFINITO.csv` con motivazione: `DA_VALUTARE` è intenzionale nei casi ambigui. Congelare le modifiche al gold prima di usare gli output per la valutazione. Non inviare il gold al modello.

## Esecuzione su macOS

```bash
cd "$HOME/Desktop/validazione_holdout_uc01_v01"
bash esegui.command
```

Il programma genera `risultati/holdout_baseline_vs_candidata_.../` con `manifest.json`, `confronto_note.csv`, `confronto_frammenti.csv`, `revisione_note.csv`, `report.md` e dettagli diagnostici. Se il modello o il runtime hanno hash diversi dall'esperimento S0/S1 precedente, il programma si ferma per proteggere la comparabilità. In quel caso non sostituire i file congelati: segnalare la differenza.

## Controllo metodologico

- X0 viene eseguito **una sola volta** per nota, e riutilizzato per C0 e C2.
- La baseline usa S0; la candidata usa S1 sugli output C2. Z resta invariato.
- La variabile tra le due configurazioni è **il pacchetto C+S**, non il solo selettore: il confronto misura l'effetto combinato, non attribuisce causalmente un miglioramento a C2 oppure S1.
- Valutazione primaria a livello nota: proposta appropriata e autonoma, proposta indebita, oppure omissione di attività proposta; annotare separatamente le date incomplete, i casi multi-task e gli errori X0.
- Se si vogliono attribuzioni tra componenti, i dettagli includono anche C2+S0 e permettono un'analisi secondaria *senza altre inferenze*.
- Non giudicare dal solo numero di popup. Effettuare revisione manuale (preferibilmente indipendente e cieca alla variante) delle 32 note.
- Non si effettuano scritture in calendari, note, task o servizi esterni. Nessuna inferenza effettiva è stata eseguita nella preparazione di questo pacchetto.
