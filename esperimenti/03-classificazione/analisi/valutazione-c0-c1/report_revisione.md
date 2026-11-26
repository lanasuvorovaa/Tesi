# Revisione semantica manuale C0 vs C1 — Development UC-01

**Data:** 20 novembre 2026. **Fonte:** risultati del pacchetto `classificazione_c1_qwen3_uc01_v01(1).zip`. I due CSV originali sono stati compilati senza cambiare le predizioni né i dati osservati. Valutazione interpretativa ex post, non test indipendente e non nuova esecuzione del modello.

## Criterio di annotazione

La label gold assegna `kind` e `intent` al frammento **nel contesto della nota completa**, usando le sei intenzioni del prompt C1. Le azioni completate restano `TASK/COMPLETED`, mentre informazioni generiche sono `FACT/INFORMATIONAL`. Frasi riportate come citazioni sono etichettate con `INFORMATIONAL` per non trasformarle in comandi reali. Complementi isolati (date, nomi, parti di una frase) possono essere annotati come `FACT/INFORMATIONAL` anche quando la nota completa parla di un evento. Sono scelte operative di annotazione, non una gold standard preesistente: vanno condivise e congelate prima di valutazioni indipendenti.

## Conteggi su 45 frammenti

| Misura | C0 | C1 |
|---|---:|---:|
| Entrambi i campi corretti | 17/45 (37.8%) | 18/45 (40.0%) |
| Solo tipo (`kind`) corretto | 28/45 | 24/45 |
| Solo intenzione (`intent`) corretta | 21/45 | 25/45 |

- Errori C0 corretti da C1: **8**.
- Classificazioni C0 corrette peggiorate da C1: **7**.
- Corrette per entrambe: **10**.
- Errate per entrambe: **20**.

## Esiti su 24 note

- C0 migliore: **5** note.
- Parità con limite: **7** note.
- Parità: **11** note.
- Parità errata: **1** note.

**Interpretazione:** i conteggi di popup (11 per condizione) non misurano la correttezza. Alcuni popup condivisi sono parziali, e due falsi positivi C1 sostituiscono due attività reali che C1 non propone più. Per il dettaglio dei 24 esiti consultare `revisione_note_compilata.csv`.

## Attribuzione diagnostica dei problemi

Le categorie seguenti **si sovrappongono**: descrivono contributi plausibili dei componenti, non effetti causali misurati con ablation test.

- **X0 / frammentazione contestuale:** UC01-MAIN-002, UC01-MAIN-062, UC01-MAIN-076.
- **C0 e C1 / errori di classificazione:** UC01-MAIN-022, UC01-MAIN-024, UC01-MAIN-060, UC01-MAIN-062, UC01-MAIN-094, UC01-MAIN-095.
- **C1 / nuovi falsi positivi o falsi negativi:** UC01-MAIN-076, UC01-MAIN-097, UC01-MAIN-113, UC01-MAIN-118.
- **Z / protezione utile su citazioni:** UC01-MAIN-022, UC01-MAIN-095.
- **S / selezione di un frammento parziale o non autonomo:** UC01-MAIN-062, UC01-MAIN-076, UC01-MAIN-113.
- **S / singolo popup a fronte di più attività:** UC01-MAIN-011, UC01-MAIN-024, UC01-MAIN-062.
- **Chiarimento dati temporali mancanti:** UC01-MAIN-052, UC01-MAIN-080.

### Distinzione tra X0, C, Z e S

- **X0:** spezza vincoli temporali, alternative o espressioni collegate; ciò limita la completezza della proposta (002, 062, 076). Non risulta un errore di estrazione generalizzato: i frammenti critici spesso sono presenti, ma decontestualizzati.
- **C:** responsabile diretto di etichette errate, tra cui `FACT` invece di `TASK` per la mail (060), `FACT` invece di `TASK` per il modulo in C1 (097), e `COMPLETED` per il controllo futuro in C1 (118).
- **Z:** correttamente interdice i comandi contenuti in testi citati (022, 095); il gate di 097 blocca coerentemente un candidato `FACT`, quindi la causa iniziale è C1. Il gate usato nel confronto è quello *sandbox*: l'`actual_gate` verifica anche capability e duplicati e non corrisponde alla decisione popup del benchmark.
- **S:** sceglie un solo candidato; in 062 seleziona un'intestazione nominale senza ora, mentre in 076 e 113 lascia passare frammenti non autosufficienti sotto C1. Il numero uno di popup per nota è un vincolo del test, non necessariamente un bug.

## Decisione sperimentale

**Non adottare C1 nella baseline.** C0 mantiene i task di 097 e 118 e non produce i popup spuri di 076 e 113. C1 migliora alcuni frammenti ma introduce regressioni importanti. Conservare X0+C0+Z+S; per una C2 futura concentrarsi su negazioni, obblighi impliciti, completamento temporale e protezione dei frammenti isolati, poi valutare su un set non usato nella progettazione.

## Limiti

Questa è una revisione manuale effettuata dall'assistente, non una validazione con annotatori indipendenti. Le etichette di frammenti isolati e i casi fuori dominio (es. playlist) possono ammettere convenzioni differenti. Le statistiche dipendono dalle convenzioni documentate qui. Non vengono attribuite prestazioni a componenti con prove controfattuali non eseguite.
