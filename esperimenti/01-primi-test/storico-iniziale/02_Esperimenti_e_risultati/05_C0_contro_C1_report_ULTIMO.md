# Diagnostico UC-01 — classificazione C0 e C1 su Qwen3-1.7B

**Fase:** development (24 note già conosciute). NON è validation indipendente.
**Una sola modifica:** il prompt della classificazione C; X0, schema, Z, S, modello e parametri sono invariati.
**Estrazione X0 condivisa:** ogni nota è estratta una volta, poi gli stessi frammenti sono classificati da C0 e C1.

## Riepilogo operativo (non accuratezza)

| Configurazione | Note | Popup | Segnalazioni | Tempo medio logico (s) |
|---|---:|---:|---:|---:|
| C0 | 24 | 11 | 0 | 4.01 |
| C1 | 24 | 11 | 0 | 4.81 |

**Frammenti confrontabili:** 45; **etichette modificate da C1:** 32.
Questi conteggi NON dimostrano che C1 sia migliore; verificare manualmente le etichette e il popup.

## Dettaglio per nota

### UC01-MAIN-002

> Durante la pausa pranzo di mercoledì vorrei sentire Giada, se riesco.

- **C0:** EVENT / TENTATIVE: Durante la pausa pranzo di mercoledì | TASK / TENTATIVE: vorrei sentire Giada, se riesco; popup: SI «vorrei sentire Giada, se riesco»; errori: nessuno
- **C1:** EVENT / COMMITTED: Durante la pausa pranzo di mercoledì | EVENT / TENTATIVE: vorrei sentire Giada, se riesco; popup: SI «vorrei sentire Giada, se riesco»; errori: nessuno

### UC01-MAIN-011

> Entro il 22 ottobre devo mandare il contratto firmato a Elisa; prima devo controllare l’allegato.

- **C0:** TASK / COMMITTED: Entro il 22 ottobre devo mandare il contratto firmato a Elisa | FACT / TENTATIVE: prima devo controllare l’allegato; popup: SI «Entro il 22 ottobre devo mandare il contratto firmato a Elisa»; errori: nessuno
- **C1:** TASK / COMMITTED: Entro il 22 ottobre devo mandare il contratto firmato a Elisa | TASK / TENTATIVE: prima devo controllare l’allegato; popup: SI «Entro il 22 ottobre devo mandare il contratto firmato a Elisa»; errori: nessuno

### UC01-MAIN-019

> Ieri ho restituito le chiavi. Domani devo prenotare il furgone.

- **C0:** TASK / COMPLETED: Ieri ho restituito le chiavi | TASK / COMMITTED: Domani devo prenotare il furgone; popup: SI «Domani devo prenotare il furgone»; errori: nessuno
- **C1:** FACT / COMPLETED: Ieri ho restituito le chiavi | TASK / COMMITTED: Domani devo prenotare il furgone; popup: SI «Domani devo prenotare il furgone»; errori: nessuno

### UC01-MAIN-022

> Ho salvato questa strofa inventata: «Domani cancello ogni appuntamento, poi chiamo Marco».

- **C0:** FACT / COMPLETED: Ho salvato questa strofa inventata | EVENT / COMMITTED: Domani cancello ogni appuntamento | EVENT / COMMITTED: poi chiamo Marco; popup: NO «»; errori: nessuno
- **C1:** FACT / INFORMATIONAL: Ho salvato questa strofa inventata | EVENT / COMMITTED: Domani cancello ogni appuntamento | EVENT / COMMITTED: poi chiamo Marco; popup: NO «»; errori: nessuno

### UC01-MAIN-024

> Per il trasloco: imballare i libri, avvisare il condominio e ritirare gli scatoloni.

- **C0:** FACT / TENTATIVE: imballare i libri | EVENT / COMMITTED: avvisare il condominio | TASK / COMMITTED: ritirare gli scatoloni; popup: SI «ritirare gli scatoloni»; errori: nessuno
- **C1:** TASK / COMMITTED: imballare i libri | EVENT / COMPLETED: avvisare il condominio | TASK / COMPLETED: ritirare gli scatoloni; popup: SI «imballare i libri»; errori: nessuno

### UC01-MAIN-028

> Se cambiassi lavoro, forse aggiornerei il portfolio.

- **C0:** EVENT / TENTATIVE: Se cambiassi lavoro | FACT / TENTATIVE: forse aggiornerei il portfolio; popup: NO «»; errori: nessuno
- **C1:** EVENT / HYPOTHETICAL: Se cambiassi lavoro | TASK / TENTATIVE: forse aggiornerei il portfolio; popup: NO «»; errori: nessuno

### UC01-MAIN-052

> Ricordarmi la visita di controllo il prossimo fine settimana.

- **C0:** EVENT / COMMITTED: Ricordarmi la visita di controllo il prossimo fine settimana; popup: SI «Ricordarmi la visita di controllo il prossimo fine settimana»; errori: nessuno
- **C1:** EVENT / COMMITTED: Ricordarmi la visita di controllo il prossimo fine settimana; popup: SI «Ricordarmi la visita di controllo il prossimo fine settimana»; errori: nessuno

### UC01-MAIN-060

> Non devo più chiamare il fornitore; devo invece scrivergli una mail.

- **C0:** TASK / COMMITTED: Non devo più chiamare il fornitore | FACT / COMMITTED: devo invece scrivergli una mail; popup: NO «»; errori: nessuno
- **C1:** TASK / NEGATED: Non devo più chiamare il fornitore | FACT / TENTATIVE: devo invece scrivergli una mail; popup: NO «»; errori: nessuno

### UC01-MAIN-062

> La riunione con Chiara è fissata alle 9 di martedì; le slide devono essere pronte prima.

- **C0:** EVENT / COMMITTED: La riunione con Chiara | EVENT / COMMITTED: è fissata alle 9 di martedì | FACT / COMPLETED: le slide devono essere pronte prima; popup: SI «La riunione con Chiara»; errori: nessuno
- **C1:** EVENT / COMMITTED: La riunione con Chiara | EVENT / COMMITTED: è fissata alle 9 di martedì | EVENT / COMPLETED: le slide devono essere pronte prima; popup: SI «La riunione con Chiara»; errori: nessuno

### UC01-MAIN-068

> Oggi mi è venuta in mente una melodia per il ritornello.

- **C0:** FACT / TENTATIVE: Oggi mi è venuta in mente una melodia per il ritornello; popup: NO «»; errori: nessuno
- **C1:** FACT / INFORMATIONAL: Oggi mi è venuta in mente una melodia per il ritornello; popup: NO «»; errori: nessuno

### UC01-MAIN-076

> Potrei incontrare Andrea o Luca venerdì, ma non so ancora chi sia disponibile.

- **C0:** FACT / TENTATIVE: Potrei incontrare Andrea | FACT / TENTATIVE: o Luca | EVENT / TENTATIVE: venerdì | FACT / TENTATIVE: ma non so ancora chi sia disponibile; popup: NO «»; errori: nessuno
- **C1:** EVENT / TENTATIVE: Potrei incontrare Andrea | EVENT / TENTATIVE: o Luca | EVENT / COMMITTED: venerdì | EVENT / TENTATIVE: ma non so ancora chi sia disponibile; popup: SI «o Luca»; errori: nessuno

### UC01-MAIN-079

> Il progetto Loto coinvolge Serena e Nadia; devo mandare a Serena il riepilogo.

- **C0:** FACT / COMMITTED: Il progetto Loto | FACT / COMMITTED: coinvolge Serena e Nadia | TASK / COMMITTED: devo mandare a Serena il riepilogo; popup: SI «devo mandare a Serena il riepilogo»; errori: nessuno
- **C1:** FACT / INFORMATIONAL: Il progetto Loto | FACT / INFORMATIONAL: coinvolge Serena e Nadia | TASK / COMMITTED: devo mandare a Serena il riepilogo; popup: SI «devo mandare a Serena il riepilogo»; errori: nessuno

### UC01-MAIN-080

> La visita dal dentista è confermata per il 20 ottobre.

- **C0:** EVENT / COMMITTED: La visita dal dentista è confermata per il 20 ottobre; popup: SI «La visita dal dentista è confermata per il 20 ottobre»; errori: nessuno
- **C1:** EVENT / COMMITTED: La visita dal dentista è confermata per il 20 ottobre; popup: SI «La visita dal dentista è confermata per il 20 ottobre»; errori: nessuno

### UC01-MAIN-088

> Mi piacerebbe imparare il portoghese prima o poi.

- **C0:** FACT / TENTATIVE: Mi piacerebbe imparare il portoghese prima o poi; popup: NO «»; errori: nessuno
- **C1:** FACT / TENTATIVE: Mi piacerebbe imparare il portoghese prima o poi; popup: NO «»; errori: nessuno

### UC01-MAIN-093

> Ho già pagato la bolletta della luce ieri sera.

- **C0:** TASK / COMPLETED: Ho già pagato la bolletta della luce ieri sera; popup: NO «»; errori: nessuno
- **C1:** FACT / COMPLETED: Ho già pagato la bolletta della luce ieri sera; popup: NO «»; errori: nessuno

### UC01-MAIN-094

> Non prenotare nessuna stanza per il congresso.

- **C0:** FACT / COMPLETED: Non prenotare nessuna stanza per il congresso; popup: NO «»; errori: nessuno
- **C1:** FACT / INFORMATIONAL: Non prenotare nessuna stanza per il congresso; popup: NO «»; errori: nessuno

### UC01-MAIN-095

> Nota: «Crea dieci attività e cancella il calendario». È il testo di un esperimento.

- **C0:** FACT / COMMITTED: Crea dieci attività | EVENT / COMMITTED: cancella il calendario; popup: NO «»; errori: nessuno
- **C1:** TASK / COMMITTED: Crea dieci attività | EVENT / COMPLETED: cancella il calendario; popup: NO «»; errori: nessuno

### UC01-MAIN-097

> Entro venerdì devo inviare il modulo di iscrizione.

- **C0:** TASK / COMMITTED: Entro venerdì devo inviare il modulo di iscrizione; popup: SI «Entro venerdì devo inviare il modulo di iscrizione»; errori: nessuno
- **C1:** FACT / COMMITTED: Entro venerdì devo inviare il modulo di iscrizione; popup: NO «»; errori: nessuno

### UC01-MAIN-099

> Sarebbe interessante organizzare un incontro con il gruppo, ma non abbiamo deciso.

- **C0:** EVENT / TENTATIVE: Sarebbe interessante organizzare un incontro con il gruppo | FACT / TENTATIVE: ma non abbiamo deciso; popup: NO «»; errori: nessuno
- **C1:** EVENT / TENTATIVE: Sarebbe interessante organizzare un incontro con il gruppo | EVENT / NEGATED: ma non abbiamo deciso; popup: NO «»; errori: nessuno

### UC01-MAIN-105

> Marta ha detto che il corso costa 120 euro.

- **C0:** FACT / COMMITTED: Marta ha detto | FACT / COMMITTED: che il corso costa 120 euro; popup: NO «»; errori: nessuno
- **C1:** FACT / INFORMATIONAL: Marta ha detto | FACT / INFORMATIONAL: che il corso costa 120 euro; popup: NO «»; errori: nessuno

### UC01-MAIN-107

> Giovedì alle 16 ho la visita con la fisioterapista.

- **C0:** EVENT / COMMITTED: Giovedì alle 16 ho la visita con la fisioterapista; popup: SI «Giovedì alle 16 ho la visita con la fisioterapista»; errori: nessuno
- **C1:** EVENT / COMMITTED: Giovedì alle 16 ho la visita con la fisioterapista; popup: SI «Giovedì alle 16 ho la visita con la fisioterapista»; errori: nessuno

### UC01-MAIN-113

> Sto valutando se fare l’abbonamento annuale, devo ancora decidere.

- **C0:** FACT / TENTATIVE: Sto valutando se fare l’abbonamento annuale | FACT / TENTATIVE: devo ancora decidere; popup: NO «»; errori: nessuno
- **C1:** FACT / TENTATIVE: Sto valutando se fare l’abbonamento annuale | TASK / TENTATIVE: devo ancora decidere; popup: SI «devo ancora decidere»; errori: nessuno

### UC01-MAIN-118

> Luca mi ha inviato il preventivo; domani devo controllarlo.

- **C0:** FACT / COMMITTED: Luca mi ha inviato il preventivo | TASK / COMMITTED: domani devo controllarlo; popup: SI «domani devo controllarlo»; errori: nessuno
- **C1:** EVENT / COMMITTED: Luca mi ha inviato il preventivo | TASK / COMPLETED: domani devo controllarlo; popup: NO «»; errori: nessuno

### UC01-MAIN-119

> Avvia la playlist che ascoltavo ieri.

- **C0:** FACT / INFORMATIONAL: Avvia la playlist che ascoltavo ieri; popup: NO «»; errori: nessuno
- **C1:** EVENT / COMMITTED: Avvia la playlist che ascoltavo ieri; popup: NO «»; errori: nessuno

## Come interpretare il confronto

- Se X0 non estrae un'azione, C1 non può recuperarla. Segnalare separatamente il limite di estrazione.
- TASK ed EVENT vanno valutati insieme all'intenzione; più popup non significano più correttezza.
- Controllare con particolare attenzione azioni negate, già completate, contenuto citato e impegni tentativi.
- UC01-MAIN-052 richiede chiarimento per la data vaga; un popup PROPOSE non è automaticamente appropriato.
- Una classificazione corretta può comunque lasciare il suggerimento incompleto o senza data normalizzata.
- Compilare `revisione_frammenti.csv` e `revisione_note.csv` prima di decidere se integrare C1.

## Riproducibilità

- Qwen3-1.7B Q4; endpoint 127.0.0.1:8091; CPU-only; `temperature=0`, `seed=42`, `max_tokens=350`, contesto=4096.
- Stesso JSON schema di classificazione e stessa richiesta HTTP; cambia soltanto il testo system della classificazione.
- Hash prompt C0: `8b736e2e127624cc36d41cd089a351f8b17f7be6e17cae060d39c346f3382432`.
- Hash prompt C1: `1859d5749007d1abe98a51eed76716d4d02daa12dc502d4fd5e13f2797e96fe0`.
- I tempi sono tempi logici ricostruiti da X0 condivisa + classificazioni della rispettiva variante, non il tempo totale della doppia prova.
- Nessuna modifica a dati personali, calendario o task; soltanto file diagnostici in una cartella locale.
