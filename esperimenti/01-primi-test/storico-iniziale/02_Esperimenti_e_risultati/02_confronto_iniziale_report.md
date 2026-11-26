# Confronto modelli — UC-01

Fase: **1**. Risultati di sviluppo, non validation né test.

I conteggi indicano il comportamento della pipeline e NON la correttezza semantica. Compilare revisione_manuale.csv.

| Modello | Casi | Errori/segnalazioni | Popup | Tempo medio (s, casi eseguiti) |
|---|---:|---:|---:|---:|
| qwen3-1.7b | 10 | 0 | 8 | 5.54 |
| qwen3.5-2b | 10 | 3 | 6 | 17.11 |
| lfm2.5-1.2b | 10 | 1 | 9 | 9.6 |

## Lettura del risultato

- La differenza tra 'popup' e 'candidato corretto' è essenziale: un popup può essere semanticamente errato.
- Controllare separatamente estrazione, tipo, intenzione, gate Z e scelta del selettore.
- JSON vincolato/non valido o errori server sono problemi di compatibilità della pipeline, non prova di incapacità linguistica.
- In questa prova tutti i modelli ricevono gli stessi prompt e parametri, senza ottimizzazioni per famiglia.
- Tutti i modelli usano il medesimo runtime aggiornato CPU; la demo originale non viene sostituita.
- Le misure di tempo riguardano questo Mac Intel, non uno smartphone Android.

## Riproducibilità

- Endpoint temporaneo: 127.0.0.1:8091.
- temperature=0; seed=42; max_tokens=350; contesto server=4096; CPU-only.
- Manifest: `manifest.json`; codice congelato sha256: `7b57cf9bab1df3be4e77d2fcf55263cd22bf2e72893f116d160ef4de96af7f61`.
- Nessuna scrittura su note, attività, calendario o servizi cloud. Vengono creati soltanto questi file di report.

## Risultati per nota

### RIUNIONE-00

- **qwen3-1.7b**: 3 frammenti, 3 candidati; popup: SI (EVENT, «La riunione con Chiara»); 10.72 s; stato=ESEGUITO
- **qwen3.5-2b**: 10 frammenti, 10 candidati; popup: NO (, «»); 27.29 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «le slide devono essere pronte prima»); 9.69 s; stato=ESEGUITO

### RIUNIONE-01

- **qwen3-1.7b**: 2 frammenti, 2 candidati; popup: SI (EVENT, «Martedì alle 9 ho una riunione con Chiara»); 4.66 s; stato=ESEGUITO
- **qwen3.5-2b**: 12 frammenti, 12 candidati; popup: SI (TASK, «devo»); 24.16 s; stato=SEGNALAZIONI — QUOTE_8_INVALID_OR_NOT_UNIQUE | QUOTE_11_INVALID_OR_NOT_UNIQUE
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «devo preparare le slide prima»); 10.41 s; stato=ESEGUITO

### RIUNIONE-02

- **qwen3-1.7b**: 3 frammenti, 3 candidati; popup: SI (TASK, «Devo finire le slide»); 5.99 s; stato=ESEGUITO
- **qwen3.5-2b**: 12 frammenti, 12 candidati; popup: SI (TASK, «Devo»); 23.68 s; stato=SEGNALAZIONI — QUOTE_2_INVALID_OR_NOT_UNIQUE | QUOTE_6_INVALID_OR_NOT_UNIQUE
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «Devo finire le slide prima della riunione con Chiara»); 10.46 s; stato=ESEGUITO

### RIUNIONE-03

- **qwen3-1.7b**: 2 frammenti, 2 candidati; popup: SI (EVENT, «Per martedì alle 9 è fissata la riunione con Chiara»); 5.17 s; stato=ESEGUITO
- **qwen3.5-2b**: 2 frammenti, 2 candidati; popup: NO (, «»); 6.07 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «Per martedì alle 9 è fissata la riunione con Chiara»); 10.41 s; stato=ESEGUITO

### RIUNIONE-04

- **qwen3-1.7b**: 3 frammenti, 3 candidati; popup: SI (EVENT, «vedrò Chiara in riunione»); 6.29 s; stato=ESEGUITO
- **qwen3.5-2b**: 5 frammenti, 5 candidati; popup: SI (TASK, «Prima devo»); 11.26 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «Prima devo completare le slide»); 10.58 s; stato=ESEGUITO

### RIUNIONE-05

- **qwen3-1.7b**: 1 frammenti, 1 candidati; popup: SI (EVENT, «La riunione con Chiara sarà martedì alle 9; prima di allora devo avere le slide pronte»); 4.37 s; stato=ESEGUITO
- **qwen3.5-2b**: 3 frammenti, 3 candidati; popup: SI (TASK, «prima di allora devo avere le slide pronte»); 8.03 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «devo avere le slide pronte»); 10.51 s; stato=ESEGUITO

### UC01-MAIN-019

- **qwen3-1.7b**: 2 frammenti, 2 candidati; popup: SI (TASK, «Domani devo prenotare il furgone»); 4.94 s; stato=ESEGUITO
- **qwen3.5-2b**: 10 frammenti, 10 candidati; popup: SI (TASK, «devo»); 21.96 s; stato=SEGNALAZIONI — QUOTE_5_INVALID_OR_NOT_UNIQUE
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «Domani devo prenotare il furgone»); 10.48 s; stato=ESEGUITO

### UC01-MAIN-022

- **qwen3-1.7b**: 3 frammenti, 3 candidati; popup: NO (, «»); 5.82 s; stato=ESEGUITO
- **qwen3.5-2b**: 12 frammenti, 12 candidati; popup: NO (, «»); 25.12 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 1 frammenti, 1 candidati; popup: NO (, «»); 6.52 s; stato=SEGNALAZIONI — QUOTE_1_INVALID_OR_NOT_UNIQUE

### UC01-MAIN-052

- **qwen3-1.7b**: 1 frammenti, 1 candidati; popup: SI (EVENT, «Ricordarmi la visita di controllo il prossimo fine settimana»); 3.11 s; stato=ESEGUITO
- **qwen3.5-2b**: 9 frammenti, 9 candidati; popup: SI (TASK, «Ricordarmi»); 17.74 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 1 frammenti, 1 candidati; popup: SI (TASK, «Ricordarmi la visita di controllo il prossimo fine settimana.»); 6.45 s; stato=ESEGUITO

### UC01-MAIN-060

- **qwen3-1.7b**: 2 frammenti, 2 candidati; popup: NO (, «»); 4.37 s; stato=ESEGUITO
- **qwen3.5-2b**: 2 frammenti, 2 candidati; popup: NO (, «»); 5.78 s; stato=ESEGUITO
- **lfm2.5-1.2b**: 2 frammenti, 2 candidati; popup: SI (TASK, «devo invece scrivergli una mail»); 10.44 s; stato=ESEGUITO

