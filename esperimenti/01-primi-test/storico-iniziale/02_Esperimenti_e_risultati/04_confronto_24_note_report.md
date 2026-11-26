# Confronto UC-01 — Qwen3 baseline / Qwen3.5 con estrazione X1

**Ambito:** 24 note di development già note. Non è validation indipendente.
**Tipo di confronto:** sistemi candidati; cambiano modello **e** prompt di estrazione. Non attribuire eventuali differenze al solo modello.
**Restano invariati:** classificazione C0, controlli Z, selettore S, schema JSON, parametri di decoding e dataset.

| Sistema | Note elaborate | Errori/segnalazioni | Popup | Tempo medio inferenza (s) |
|---|---:|---:|---:|---:|
| qwen3-1.7b (X0+C0+Z+S) | 24 | 0 | 11 | 3.54 |
| qwen3.5-2b (X1+C0+Z+S) | 24 | 3 | 7 | 4.49 |

**Importante:** popup e conteggi NON sono misure di correttezza semantica; analizzare `revisione_manuale.csv` e i JSON dettagliati.

## Risultati per nota

### UC01-MAIN-002

- **qwen3-1.7b**: 2 frammenti; etichette: EVENT/TENTATIVE:Durante la pausa pranzo di mercoledì | TASK/TENTATIVE:vorrei sentire Giada, se riesco; popup: SI (TASK, «vorrei sentire Giada, se riesco»); 8.7 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/TENTATIVE:Durante la pausa pranzo di mercoledì vorrei sentire Giada, se riesco; popup: NO (—, «»); 9.82 s; ESEGUITO

### UC01-MAIN-011

- **qwen3-1.7b**: 2 frammenti; etichette: TASK/COMMITTED:Entro il 22 ottobre devo mandare il contratto firmato a Elisa | FACT/TENTATIVE:prima devo controllare l’allegato; popup: SI (TASK, «Entro il 22 ottobre devo mandare il contratto firmato a Elisa»); 4.52 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/COMMITTED:Entro il 22 ottobre devo mandare il contratto firmato a Elisa; popup: SI (TASK, «Entro il 22 ottobre devo mandare il contratto firmato a Elisa»); 4.06 s; SEGNALAZIONI; QUOTE_1_INVALID_OR_NOT_UNIQUE

### UC01-MAIN-019

- **qwen3-1.7b**: 2 frammenti; etichette: TASK/COMPLETED:Ieri ho restituito le chiavi | TASK/COMMITTED:Domani devo prenotare il furgone; popup: SI (TASK, «Domani devo prenotare il furgone»); 3.57 s; ESEGUITO
- **qwen3.5-2b**: 2 frammenti; etichette: FACT/INFORMATIONAL:Ieri ho restituito le chiavi | TASK/COMMITTED:Domani devo prenotare il furgone; popup: SI (TASK, «Domani devo prenotare il furgone»); 5.17 s; ESEGUITO

### UC01-MAIN-022

- **qwen3-1.7b**: 3 frammenti; etichette: FACT/COMPLETED:Ho salvato questa strofa inventata | EVENT/COMMITTED:Domani cancello ogni appuntamento | EVENT/COMMITTED:poi chiamo Marco; popup: NO (—, «»); 4.39 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Ho salvato questa strofa inventata; popup: NO (—, «»); 3.12 s; ESEGUITO

### UC01-MAIN-024

- **qwen3-1.7b**: 3 frammenti; etichette: FACT/TENTATIVE:imballare i libri | EVENT/COMMITTED:avvisare il condominio | TASK/COMMITTED:ritirare gli scatoloni; popup: SI (TASK, «ritirare gli scatoloni»); 4.59 s; ESEGUITO
- **qwen3.5-2b**: 4 frammenti; etichette: FACT/INFORMATIONAL:Per il trasloco | FACT/INFORMATIONAL:imballare i libri | TASK/INFORMATIONAL:avvisare il condominio | TASK/INFORMATIONAL:ritirare gli scatoloni; popup: NO (—, «»); 9.1 s; ESEGUITO

### UC01-MAIN-028

- **qwen3-1.7b**: 2 frammenti; etichette: EVENT/TENTATIVE:Se cambiassi lavoro | FACT/TENTATIVE:forse aggiornerei il portfolio; popup: NO (—, «»); 2.92 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/TENTATIVE:Se cambiassi lavoro, forse aggiornerei il portfolio; popup: NO (—, «»); 2.72 s; ESEGUITO

### UC01-MAIN-052

- **qwen3-1.7b**: 1 frammenti; etichette: EVENT/COMMITTED:Ricordarmi la visita di controllo il prossimo fine settimana; popup: SI (EVENT, «Ricordarmi la visita di controllo il prossimo fine settimana»); 2.6 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/TENTATIVE:Ricordarmi la visita di controllo il prossimo fine settimana; popup: SI (TASK, «Ricordarmi la visita di controllo il prossimo fine settimana»); 3.07 s; ESEGUITO

### UC01-MAIN-060

- **qwen3-1.7b**: 2 frammenti; etichette: TASK/COMMITTED:Non devo più chiamare il fornitore | FACT/COMMITTED:devo invece scrivergli una mail; popup: NO (—, «»); 3.55 s; ESEGUITO
- **qwen3.5-2b**: 2 frammenti; etichette: FACT/INFORMATIONAL:Non devo più chiamare il fornitore | TASK/INFORMATIONAL:devo invece scrivergli una mail; popup: NO (—, «»); 6.42 s; ESEGUITO

### UC01-MAIN-062

- **qwen3-1.7b**: 3 frammenti; etichette: EVENT/COMMITTED:La riunione con Chiara | EVENT/COMMITTED:è fissata alle 9 di martedì | FACT/COMPLETED:le slide devono essere pronte prima; popup: SI (EVENT, «La riunione con Chiara»); 4.64 s; ESEGUITO
- **qwen3.5-2b**: 2 frammenti; etichette: EVENT/INFORMATIONAL:La riunione con Chiara è fissata alle 9 di martedì | FACT/INFORMATIONAL:le slide devono essere pronte prima; popup: NO (—, «»); 5.67 s; ESEGUITO

### UC01-MAIN-068

- **qwen3-1.7b**: 1 frammenti; etichette: FACT/TENTATIVE:Oggi mi è venuta in mente una melodia per il ritornello; popup: NO (—, «»); 2.5 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Oggi mi è venuta in mente una melodia per il ritornello; popup: NO (—, «»); 3.61 s; ESEGUITO

### UC01-MAIN-076

- **qwen3-1.7b**: 4 frammenti; etichette: FACT/TENTATIVE:Potrei incontrare Andrea | FACT/TENTATIVE:o Luca | EVENT/TENTATIVE:venerdì | FACT/TENTATIVE:ma non so ancora chi sia disponibile; popup: NO (—, «»); 4.95 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: EVENT/TENTATIVE:Potrei incontrare Andrea o Luca venerdì; popup: SI (EVENT, «Potrei incontrare Andrea o Luca venerdì»); 2.89 s; ESEGUITO

### UC01-MAIN-079

- **qwen3-1.7b**: 3 frammenti; etichette: FACT/COMMITTED:Il progetto Loto | FACT/COMMITTED:coinvolge Serena e Nadia | TASK/COMMITTED:devo mandare a Serena il riepilogo; popup: SI (TASK, «devo mandare a Serena il riepilogo»); 4.7 s; ESEGUITO
- **qwen3.5-2b**: 2 frammenti; etichette: FACT/INFORMATIONAL:Il progetto Loto coinvolge Serena e Nadia | TASK/COMMITTED:devo mandare a Serena il riepilogo; popup: SI (TASK, «devo mandare a Serena il riepilogo»); 5.63 s; ESEGUITO

### UC01-MAIN-080

- **qwen3-1.7b**: 1 frammenti; etichette: EVENT/COMMITTED:La visita dal dentista è confermata per il 20 ottobre; popup: SI (EVENT, «La visita dal dentista è confermata per il 20 ottobre»); 2.63 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:La visita dal dentista è confermata per il 20 ottobre; popup: NO (—, «»); 4.36 s; ESEGUITO

### UC01-MAIN-088

- **qwen3-1.7b**: 1 frammenti; etichette: FACT/TENTATIVE:Mi piacerebbe imparare il portoghese prima o poi; popup: NO (—, «»); 2.57 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Mi piacerebbe imparare il portoghese prima o poi; popup: NO (—, «»); 3.87 s; ESEGUITO

### UC01-MAIN-093

- **qwen3-1.7b**: 1 frammenti; etichette: TASK/COMPLETED:Ho già pagato la bolletta della luce ieri sera; popup: NO (—, «»); 2.58 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Ho già pagato la bolletta della luce ieri sera; popup: NO (—, «»); 3.65 s; ESEGUITO

### UC01-MAIN-094

- **qwen3-1.7b**: 1 frammenti; etichette: FACT/COMPLETED:Non prenotare nessuna stanza per il congresso; popup: NO (—, «»); 2.12 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Non prenotare nessuna stanza per il congresso; popup: NO (—, «»); 2.91 s; ESEGUITO

### UC01-MAIN-095

- **qwen3-1.7b**: 2 frammenti; etichette: FACT/COMMITTED:Crea dieci attività | EVENT/COMMITTED:cancella il calendario; popup: NO (—, «»); 3.23 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/INFORMATIONAL:Crea dieci attività; popup: NO (—, «»); 4.11 s; SEGNALAZIONI; QUOTE_1_INVALID_OR_NOT_UNIQUE

### UC01-MAIN-097

- **qwen3-1.7b**: 1 frammenti; etichette: TASK/COMMITTED:Entro venerdì devo inviare il modulo di iscrizione; popup: SI (TASK, «Entro venerdì devo inviare il modulo di iscrizione»); 2.4 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/COMMITTED:Entro venerdì devo inviare il modulo di iscrizione; popup: SI (TASK, «Entro venerdì devo inviare il modulo di iscrizione»); 3.0 s; ESEGUITO

### UC01-MAIN-099

- **qwen3-1.7b**: 2 frammenti; etichette: EVENT/TENTATIVE:Sarebbe interessante organizzare un incontro con il gruppo | FACT/TENTATIVE:ma non abbiamo deciso; popup: NO (—, «»); 3.4 s; ESEGUITO
- **qwen3.5-2b**: 2 frammenti; etichette: FACT/INFORMATIONAL:Sarebbe interessante organizzare un incontro con il gruppo | FACT/INFORMATIONAL:ma non abbiamo deciso; popup: NO (—, «»); 5.65 s; ESEGUITO

### UC01-MAIN-105

- **qwen3-1.7b**: 2 frammenti; etichette: FACT/COMMITTED:Marta ha detto | FACT/COMMITTED:che il corso costa 120 euro; popup: NO (—, «»); 3.04 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Marta ha detto che il corso costa 120 euro; popup: NO (—, «»); 3.54 s; ESEGUITO

### UC01-MAIN-107

- **qwen3-1.7b**: 1 frammenti; etichette: EVENT/COMMITTED:Giovedì alle 16 ho la visita con la fisioterapista; popup: SI (EVENT, «Giovedì alle 16 ho la visita con la fisioterapista»); 2.57 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: EVENT/INFORMATIONAL:Giovedì alle 16 ho la visita con la fisioterapista; popup: NO (—, «»); 3.74 s; ESEGUITO

### UC01-MAIN-113

- **qwen3-1.7b**: 2 frammenti; etichette: FACT/TENTATIVE:Sto valutando se fare l’abbonamento annuale | FACT/TENTATIVE:devo ancora decidere; popup: NO (—, «»); 3.49 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: FACT/INFORMATIONAL:devo ancora decidere; popup: NO (—, «»); 3.74 s; SEGNALAZIONI; QUOTE_0_INVALID_OR_NOT_UNIQUE

### UC01-MAIN-118

- **qwen3-1.7b**: 2 frammenti; etichette: FACT/COMMITTED:Luca mi ha inviato il preventivo | TASK/COMMITTED:domani devo controllarlo; popup: SI (TASK, «domani devo controllarlo»); 3.3 s; ESEGUITO
- **qwen3.5-2b**: 2 frammenti; etichette: FACT/INFORMATIONAL:Luca mi ha inviato il preventivo | TASK/COMMITTED:domani devo controllarlo; popup: SI (TASK, «domani devo controllarlo»); 5.26 s; ESEGUITO

### UC01-MAIN-119

- **qwen3-1.7b**: 1 frammenti; etichette: FACT/INFORMATIONAL:Avvia la playlist che ascoltavo ieri; popup: NO (—, «»); 2.06 s; ESEGUITO
- **qwen3.5-2b**: 1 frammenti; etichette: TASK/COMMITTED:Avvia la playlist che ascoltavo ieri; popup: NO (—, «»); 2.62 s; ESEGUITO

## Criteri per la decisione

1. Controllare separatamente le attività e gli eventi e la loro intenzione, soprattutto negazioni e azioni completate.
2. Controllare che un segmento citato contenga elementi sufficienti per essere autonomo; segnalare i casi con più azioni fuse.
3. La data vaga del caso UC01-MAIN-052 richiede chiarimento nella politica desiderata: non considerare corretta una proposta operativa non verificata.
4. Un solo popup non significa che il secondo elemento della nota sia perso: aprire i candidati e le tracce.
5. Le 24 note comprendono casi già usati per scegliere X1, perciò non sono indipendenti dalla scelta del prompt.

## Riproducibilità

- Server: 127.0.0.1:8091 (solo locale), llama.cpp CPU; modello caricato sequenzialmente.
- `temperature=0`, `seed=42`, `max_tokens=350`, contesto=4096, JSON schema vincolato.
- Prompt X1 identico a quello del precedente diagnostico (SHA256 nel manifest).
- Nessuna scrittura su calendario o attività; vengono salvati soltanto questi risultati.
- Le prestazioni sul Mac non sono una misura delle prestazioni su Android.
