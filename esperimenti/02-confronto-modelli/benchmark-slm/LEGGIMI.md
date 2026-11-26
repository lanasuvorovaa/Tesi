# Confronto SLM — UC-01

Questa prova confronta **Qwen3-1.7B (baseline), Qwen3.5-2B e LFM2.5-1.2B-Instruct** usando gli stessi componenti X+C+Z e lo stesso selettore della demo UC-01 v0.3. Non modifica la demo. Non crea eventi, task né scritture persistenti.

## Cosa confrontiamo

- **Fase 1 (10 note):** le sei parafrasi della riunione e quattro scenari UC-01 development già usati (completato+nuova attività, testo citato, data vaga, negazione).
- **Fase 2 (24 note):** tutte le 24 note UC-01 development del pacchetto congelato. Eseguire solo dopo aver controllato gli esiti della fase 1.
- Tutti i modelli usano `temperature=0`, `seed=42`, `max_tokens=350`, schema JSON vincolato, X/C/Z e selettore invariati, contesto server 4096 token e sola CPU. Gli output del modello non contengono etichette gold.
- I file Q4 provengono da distribuzioni diverse. Un confronto semantico ragionevole non equivale a un confronto controllato delle sole architetture e non prova l'accuratezza sui dispositivi Android.

## Sul Mac, dall'inizio

Estrai `confronto_slm_uc01_v01.zip` sul Desktop e apri il Terminale.

### 1. Prepara una copia aggiornata di llama.cpp (una sola volta)

```bash
cd "$HOME/Desktop/confronto_slm_uc01_v01"
bash 01_prepara_runtime.command
```

Questo script scarica e compila una copia **separata** di `llama.cpp`, nella sottocartella `runtime/llama.cpp`. Non tocca `Tesi - documents/llama.cpp` né la demo UC-01 originale. Usa `git`, `cmake`, `clang++` e crea `.venv` Python con `jsonschema`.

Se `cmake` manca e hai Homebrew: `brew install cmake`. Se mancano git/clang++: `xcode-select --install`.

**Perché serve:** la vecchia build `llama.cpp` potrebbe non riconoscere le architetture Qwen3.5/LFM2.5. Compilare nella directory definitiva evita anche l'errore di ricerca delle librerie `.dylib` che hai già incontrato.

### 2. Scarica i due nuovi modelli (una sola volta)

```bash
bash 02_scarica_modelli.command
```

Scarica circa 2,1 GB in totale, se non già presenti, in `~/models`:

- `qwen3.5-2b-q4_k_m.gguf` — quantizzazione pubblicata da bartowski (circa 1,4 GB)
- `lfm2.5-1.2b-instruct-q4_k_m.gguf` — GGUF ufficiale Liquid AI (circa 0,7 GB)

Il modello `~/models/qwen3-1.7b-q4.gguf` rimane invariato. La procedura richiede Internet per il download dei pesi, del sorgente e delle dipendenze. L'inferenza delle note avviene invece soltanto in locale.

### 3. Esegui il confronto iniziale

```bash
bash 03_confronto_iniziale.command
```

Il programma avvia automaticamente **un modello alla volta** su `127.0.0.1:8091`. Non serve avviare manualmente i tre server. Consiglio di chiudere la vecchia demo e il server sulla porta 8080 prima della prova, per lasciare libera la CPU.

Gli esiti intermedi vengono salvati man mano. I file sono nella cartella `risultati/fase1_<data>/`:

- `report.md`: quadro sintetico, esito per nota, errori.
- `confronto.csv`: risultati di ciascun modello su ogni nota.
- `revisione_manuale.csv`: scheda per verificare la correttezza reale, non solo il popup.
- `dettagli/*.json`: risposte di estrazione, classificazione, Z e selettore.
- `manifest.json`: modelli, pesi, hash, configurazione, versione runtime.
- `*_llama.log`: problemi di avvio, se presenti.

**Mandami `report.md` e `confronto.csv` e, se ci sono problemi di formato, i JSON pertinenti.** Valuteremo insieme l'esito semantico e decideremo se procedere con la fase 2.

### 4. Solo dopo la fase 1: il confronto sulle 24 note

```bash
bash 04_confronto_development.command
```

Il risultato va in una nuova cartella `risultati/fase2_<data>/`. Non viene toccato alcun test o validation dataset.

## Precisazioni importanti

1. **Non considerare "popup mostrato" sinonimo di "nota interpretata correttamente".** Una nota può contenere due elementi e il selettore ne mostra al massimo uno. La scheda manuale registra evento, task, intenzione e adeguatezza della proposta separatamente.
2. Se un modello non gestisce il JSON vincolato o il server non parte, il risultato va segnalato come **problema di compatibilità**, non come errore linguistico. Non cambiare subito i prompt per "farlo passare".
3. La pipeline originale contiene anche una funzione che limita l'interfaccia al solo Qwen3-1.7B. Il runner passa esplicitamente al motore il modello realmente esposto dal server, senza modificare quella funzione o la logica X+C+Z.
4. Il benchmark *non* misura ancora l'efficienza sul telefono Android: occorrerà un test successivo sul dispositivo.
5. Sono dati di sviluppo già visti durante i test; il risultato **non è una validation indipendente**.
6. Le note non vengono inviate a servizi cloud; vengono inviate esclusivamente al server locale `127.0.0.1:8091` e salvate nei report locali. Non usare note personali reali durante questa prova.

## Fonti dei modelli

- https://huggingface.co/Qwen/Qwen3.5-2B
- https://huggingface.co/bartowski/Qwen_Qwen3.5-2B-GGUF
- https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF
- https://github.com/ggml-org/llama.cpp

## File di progetto conservati

La cartella `pipeline_demo/` è una copia della logica della demo v0.3: non viene modificata. Il benchmark conserva 24 note development estratte dall'archivio sperimentale preesistente `multimodel_XCZ_constrained_v01`, più sei parafrasi della precedente prova. Non include i gold del dataset.
