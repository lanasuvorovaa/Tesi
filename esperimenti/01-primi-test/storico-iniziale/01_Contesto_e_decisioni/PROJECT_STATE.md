# Stato di progetto — 20 novembre 2026

## 1. Obiettivo e confini
Tesi sperimentale su un **assistente personale on-device** eseguibile localmente. Nel lavoro svolto sono distinti **UC-01: estrazione/interpretazione di note e proposta di task/eventi** e **UC-02: relazioni**. Principio di sicurezza: l'assistente propone e chiede conferma; non esegue modifiche persistenti senza autorizzazione. Le prove diagnostiche non scrivono su agenda/task.

## 2. Hardware di riferimento
MacBook Pro Intel, CPU i7 sei core 2,6 GHz, 16 GB RAM, grafica Intel UHD 630, macOS 15.4.1, secondo contesto precedente. Il diagnostico C0/C1 usa Qwen3-1.7B Q4, CPU-only, llama.cpp locale porta 8091, temperature 0, seed 42, max_tokens 350, contesto 4096. La demo e gli esperimenti possono avere porte distinte (8080/8091). Non dare per scontato che la configurazione del Mac sia rimasta immutata.

## 3. Metodologia sperimentale concordata
Benchmark concettuale: A baseline deterministica, B SLM diretto, C SLM con retrieval, D ibrido. Dataset obiettivo 240 scenari; verificare nei materiali originali lo stato effettivo di completamento prima di dichiarare che siano stati tutti implementati o valutati. Metriche previste: qualità, sicurezza, latenza, RAM, energia; **non dichiarare metriche non misurate**.

## 4. Pipeline UC-01 e terminologia
`X` = estrazione dei frammenti dalla nota; `C` = classificazione dei frammenti (es. `FACT`, `TASK`, `EVENT` e intenzione/condizione); `Z` = regole e vincoli di ammissibilità; `S` = selettore della proposta/popup. La demo UC-01 v0.3 continua ad avere la configurazione di riferimento X0+C0+Z+S, salvo evidenze successive. Una migliore classificazione non implica da sola una proposta finale migliore, perché X può perdere informazioni e Z/S possono escludere o selezionare candidati.

## 5. Modelli confrontati
- Qwen3-1.7B: riferimento corrente, non dimostrato perfetto.
- Qwen3.5-2B: con estrazione sperimentale X1 frammenta meglio alcuni casi, ma nel confronto end-to-end non prevale sul riferimento e ha più segnalazioni.
- LFM2.5-1.2B: la classificazione ha mostrato confusione tra EVENT e TASK, anche quando si è sperimentato il prompt C1.
- In contesto iniziale risultano valutati/considerati anche Qwen3-0.6B ed EuroLLM-1.7B; nel presente archivio NON ci sono risultati aggiornati sufficienti per un loro confronto quantitativo.

## 6. Risultati verificati dei report
**Confronto iniziale, 10 note (`02_confronto_iniziale_report.md`):** Qwen3-1.7B 0 errori/segnalazioni, 8 popup, tempo medio 5,54 s; Qwen3.5-2B 3 segnalazioni, 6 popup, 17,11 s; LFM2.5-1.2B 1 segnalazione, 9 popup, 9,6 s. I popup non misurano correttezza.

**Confronto ampliato, 24 note development (`04_confronto_24_note_report.md`):** Qwen3-1.7B (X0+C0+Z+S) 0 segnalazioni, 11 popup, inferenza media 3,54 s; Qwen3.5-2B (X1+C0+Z+S) 3 segnalazioni, 7 popup, 4,49 s. Non è una validation indipendente.

**Ultima prova C0/C1 su Qwen3-1.7B (`05_C0_contro_C1_report_ULTIMO.md`):** 24 note development, 45 frammenti comparabili, 32 etichette cambiate; entrambe 11 popup e 0 segnalazioni; tempo medio logico 4,01 s per C0 contro 4,81 s per C1. Modificato soltanto il prompt di C; ogni X0 è condivisa tra condizioni. Le differenze non equivalgono a maggiore qualità.

## 7. Problemi osservati nell'ultimo esperimento
Esempi da verificare con priorità nel report originale:
- `UC01-MAIN-024`: C1 migliora l'identificazione di «imballare i libri» come TASK ma interpreta altre azioni come `COMPLETED`.
- `UC01-MAIN-060`: C1 rileva la negazione della chiamata, ma non classifica correttamente la mail da scrivere; il popup rimane assente.
- `UC01-MAIN-062`: «le slide devono essere pronte prima» viene erroneamente etichettato da C1 come EVENT/COMPLETED.
- `UC01-MAIN-076`: incertezza tra Andrea o Luca; C1 suggerisce «o Luca», un popup improprio.
- `UC01-MAIN-113`: C1 genera un popup «devo ancora decidere», discutibile.
- `UC01-MAIN-118`: C1 indica `COMPLETED` per «domani devo controllarlo» e perde il popup.
- `UC01-MAIN-052`: data vaga per visita: anche un popup formalmente consentito può richiedere chiarimento.
- `UC01-MAIN-022`: citazione testuale che non deve diventare un impegno reale.

## 8. Decisione di stato
**Non è stato approvato il passaggio da C0 a C1.** Il lavoro successivo è una valutazione manuale dei CSV, non l'integrazione automatica nel prototipo. Proteggere baseline e protocolli; distinguere development da future prove indipendenti.

## 9. Provenienza e lacune
Le cifre sono riprese dai cinque report e dai CSV effettivamente archiviati. Le indicazioni più generali su tesi, UC-02, hardware e benchmark provengono dal contesto delle conversazioni precedenti; non sostituiscono un protocollo sperimentale originale, che qui potrebbe mancare. Nessuna affermazione circa l'intero repository, l'intero dataset gold o la disponibilità locale dei modelli GGUF è verificata da questo pacchetto.
