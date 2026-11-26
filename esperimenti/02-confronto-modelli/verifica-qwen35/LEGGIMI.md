# Verifica end-to-end di Qwen3.5-2B — UC-01

Questa prova confronta due **sistemi** sulle stesse 24 note UC-01 development:

- **Riferimento:** Qwen3-1.7B con estrazione X0, classificazione C0, controlli Z e selettore S originali.
- **Candidato:** Qwen3.5-2B con l'estrazione X1 già provata nel diagnostico precedente e gli stessi C0, Z e S.

**Attenzione al significato del confronto:** cambiano sia il modello sia il prompt di estrazione. Un eventuale miglioramento è del *sistema candidato*, non una dimostrazione che il modello Qwen3.5 sia intrinsecamente superiore. Il prompt X1 è stato scelto dopo aver visto esempi di development; anche questo esperimento usa development e non è una validation indipendente.

Il confronto non modifica la vecchia demo UC-01, i file congelati, gli archivi originali o i pesi dei modelli. Non crea attività/eventi e non invia le note a servizi cloud. Salva soltanto file diagnostici nella cartella `risultati/`.

## Come eseguirlo sul Mac

**Prerequisiti:** devono essere ancora presenti sul Desktop la cartella `confronto_slm_uc01_v01` con `runtime/llama.cpp` compilato e l'ambiente `.venv`, e i due file GGUF già usati (`~/models/qwen3-1.7b-q4.gguf` e `~/models/qwen3.5-2b-q4_k_m.gguf`). Non serve reinstallare o scaricare nulla.

1. Estrai `verifica_qwen35_uc01_v01.zip` sul Desktop. Tieni chiusa, per la durata della prova, la demo web e i processi intensivi se possibile; assicurati che la porta 8091 sia libera.
2. Apri **una** finestra del Terminale ed esegui:

```bash
cd "$HOME/Desktop/verifica_qwen35_uc01_v01"
bash esegui.command
```

Il programma avvia automaticamente **un modello alla volta** sul server locale `127.0.0.1:8091` e termina soltanto i processi che ha avviato lui. Puoi vedere ogni nota che viene elaborata, con i relativi risultati. La porta 8080 della vecchia demo non viene utilizzata.

## Risultati

Al termine apri `risultati/development24_<data>/` e inviami:

- **`report.md`** — riepilogo, per modello e per singola nota.
- **`confronto.csv`** — risultati completi per nota, etichette, frammenti, popup, latenza.
- **`revisione_manuale.csv`** — foglio predisposto per il giudizio semantico, da compilare solo dopo la lettura dei risultati.

Sono disponibili anche `dettagli/*.json` con le risposte intermedie (X, C, Z, selettore), `manifest.json` con gli hash e i parametri e i log del server. Se serve spiegare un risultato ambiguo, allega anche il relativo JSON di dettaglio.

### Interpretazione

Non scegliere il modello in base al solo numero di popup. Un popup semanticamente errato, per esempio derivato da una negazione o da un'azione completata, è più grave di un suggerimento mancato. Il caso `UC01-MAIN-052` («prossimo fine settimana») va letto secondo la politica desiderata: occorre chiarire la data, non creare direttamente un appuntamento. Il prototipo può proporre un solo popup anche quando ha riconosciuto più candidati: non confondere questa scelta con un errore di estrazione.

**Obiettivo:** decidere se Qwen3.5-2B con X1 merita di sostituire il candidato attuale o se conviene concentrarsi sulla correzione di Qwen3-1.7B. Non aggiungiamo nuovi esempi al dataset e non modifichiamo la demo durante il confronto.

## Verifica del codice senza modelli

Facoltativa, se il runtime del confronto precedente è già disponibile:

```bash
"$HOME/Desktop/confronto_slm_uc01_v01/.venv/bin/python" -m unittest -v test_verifica.py
```

La verifica non misura l'accuratezza dei modelli: controlla soltanto i percorsi, il dataset e il corretto uso dei prompt.
