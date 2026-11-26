# Esperimento C2 — confronto controllato C0 vs C2

**Obiettivo:** verificare se un prompt C2 più mirato corregge regressioni C1 senza perdere le attività che C0 identificava. C2 è una proposta non ancora testata sul modello reale.

Il pacchetto deriva dall’esperimento C1. **Varia solo il prompt di classificazione** (`prompt_C2.txt`), rispetto a C0. Sono invariati X0, il modello Qwen3-1.7B, lo schema JSON, Z, S, 24 note development e parametri di inferenza. Il codice della pipeline congelata è copiato senza modifiche. Il runner è rinominato per salvare le condizioni C0 e C2 e i relativi log.

## Esecuzione (Mac)

1. Estrai la cartella `classificazione_c2_qwen3_uc01_v01` sul Desktop.
2. Mantieni sul Desktop `confronto_slm_uc01_v01` con runtime `llama.cpp` e `.venv` già utilizzati.
3. Verifica che esista `~/models/qwen3-1.7b-q4.gguf` e che la porta 8091 sia libera.
4. Dal Terminale esegui:

```bash
cd "$HOME/Desktop/classificazione_c2_qwen3_uc01_v01"
bash esegui.command
```

Lo script lancia test locali, avvia il modello sulla porta 8091, estrae ciascuna nota una sola volta con X0, applica C0 e C2 agli stessi frammenti e chiude solo il server avviato da questo esperimento. Non modifica la demo stabile né effettua scritture in calendari/task.

## Risultati attesi

Cartella `risultati/c0_vs_c2_YYYYMMDD_HHMMSS/`: `report.md`, `confronto_frammenti.csv`, `confronto_note.csv`, `revisione_frammenti.csv`, `revisione_note.csv`, `dettagli/*.json`, `manifest.json` e `llama_server.log`.

**Da riportare qui:** ZIP della cartella risultati. I CSV di revisione contengono campi vuoti per l'annotazione; non sono una valutazione automatica di correttezza.

## Criterio per decidere

Confrontare la correttezza di entrambe le etichette sui 45 frammenti (o segnalare esplicitamente eventuali differenze/errore di estrazione) e gli esiti sulle 24 note. Verificare specificamente le regressioni emerse con C1 (076, 097, 113, 118), oltre a 060, 062, 011 e ai casi citati/negati. Non adottare C2 se introduce nuovi popup spuri o perde task chiari, anche a fronte di un piccolo incremento aggregato.

Le 24 note hanno guidato la progettazione di C2: **questo è un test development, non una validazione indipendente**. Per supportare conclusioni generalizzabili, serve in seguito un set held-out non utilizzato nella progettazione, con convenzioni di annotazione fissate prima del test.
