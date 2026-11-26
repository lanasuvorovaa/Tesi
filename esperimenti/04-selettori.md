# 04 — Selettori delle proposte: S0, S1 e S2

## Da dove nasce l'idea

Dopo il lavoro sul classificatore (C2) mi sono accorta che una parte dei popup sbagliati non dipendeva dalle etichette, ma da quale frammento veniva scelto alla fine. X0 a volte spezza la nota in pezzi che, presi da soli, sembrano azioni ma non lo sono: per esempio «o Luca» (un'alternativa staccata dal resto della frase) oppure «devo ancora decidere». Il selettore S0 li proponeva comunque, perché C2 li aveva etichettati come evento o come task.

La domanda era quindi limitata al solo componente S: a parità di frammenti, etichette e decisioni di Z, un controllo in più sull'autonomia del frammento riduce i falsi popup senza perdere proposte valide? Ho affrontato la questione in più passaggi, ognuno su un insieme di note diverso.

## Cosa ho fatto

In tutte le prove il modello è Qwen3-1.7B (Q4, GGUF) in locale tramite llama.cpp, con temperatura 0, seed 42, massimo 350 token, contesto 4096, solo CPU. X0 viene eseguito una sola volta per nota e tutti i selettori ricevono gli stessi candidati. I selettori sono deterministici e non fanno nuove chiamate al modello. Resta il limite di un solo popup per nota.

1. **S0 contro S1 sulle 24 note di sviluppo.** Stessi 45 candidati prodotti una volta da X0+C2+Z. S1 conserva punteggi e divieti di S0 e aggiunge tre veti generali: connettivo isolato (`S1_DANGLING_CONNECTOR`), metadescrizione di una decisione (`S1_META_DECISION`) e stato di indecisione (`S1_UNDECIDED_STATE`).
2. **Holdout di 32 note.** 32 note sintetiche nuove rispetto alle 24 (53 frammenti X0), con un gold preparato prima. Qui ho confrontato la baseline X0+C0+Z+S0 con la candidata X0+C2+Z+S1: cambiano insieme classificatore e selettore, quindi la prova misura l'effetto combinato e non attribuisce il risultato a C2 o a S1 separatamente.
3. **Progettazione di S2.** Dagli errori dell'holdout ho ricavato tre varianti: S2-V (solo veto su aspirazioni indefinite e frasi descrittive senza azione del soggetto), S2-R (solo ranking: bonus per azione esplicita, lieve malus per descrizione o aspirazione, senza bloccare nulla) e S2-VR (le due cose insieme). Prima di eseguirle su note nuove ho fatto un replay sui candidati già noti, senza nuove inferenze.
4. **Test su 40 note nuove.** Un set sintetico di 40 note in 8 gruppi (task espliciti, eventi confermati, descrizioni simili a task, intenzioni vaghe, negazioni, multiattività, contesto frammentato, citazioni), con gold scritto prima dell'esecuzione. X0+C2+Z fissi, cambiano solo S1, S2-V, S2-R, S2-VR. La prima esecuzione si è fermata perché la data di riferimento non aveva il fuso orario; ho corretto solo quel campo (`+01:00`) prima di avere qualsiasi predizione.
5. **Chiusura di S2.** Dopo il test ho deciso la policy sul caso 029 (obblighi impersonali), rimasto aperto nel gold, e ho ricalcolato i risultati lasciando intatto il gold originale.

Per la valutazione per nota ho usato quattro categorie: A = proposta corretta e autonoma oppure corretta assenza di popup; P = proposta pertinente ma incompleta; E = errata, mancante o impropria; U = non decidibile finché non si fissa una policy.

## Cosa si vede

**S0 contro S1 (24 note di sviluppo).** I popup passano da 14 a 12. Cambiano solo due note: UC01-MAIN-076 («o Luca» → nessun popup) e UC01-MAIN-113 («devo ancora decidere» → nessun popup). Entrambe erano falsi popup; le altre 22 note hanno esattamente la stessa selezione, quindi nessuna proposta valida è stata persa. Restano problemi che S1 non può risolvere: X0 separa l'evento dal suo orario (062: «La riunione con Chiara» senza «alle 9 di martedì»), e con un solo popup in 024 si propone una delle tre attività.

**Holdout 32 (baseline X0+C0+Z+S0 contro candidata X0+C2+Z+S1).** Popup 13 e 13, selezione diversa su 6 note.

| Configurazione | A | P | E | U |
|---|---:|---:|---:|---:|
| Baseline X0+C0+Z+S0 | 18 | 5 | 7 | 2 |
| Candidata X0+C2+Z+S1 | 18 | 6 | 6 | 2 |

La candidata migliora 006, 019 e 023 (per esempio non propone più «Lo riporto per il verbale»), ma peggiora 004 (sceglie «Il commercialista aspetta i documenti» invece di «gli mando la scansione domattina») e 021 (propone «Forse un giorno aprirò una piccola libreria»). In 028 cambia solo quale delle tre attività viene proposta. Limiti comuni: 007 e 009 (eventi confermati non proposti), 016 (task non estratto da X0).

**Replay diagnostico di S2 sui set già noti.** Sulle 24 note di sviluppo nessuna variante cambia vincitore (12 popup per tutte). Sull'holdout i popup sono 13 (S1), 12 (S2-V), 13 (S2-R), 12 (S2-VR): S2-V e S2-R recuperano la scansione in 004, solo il veto elimina l'aspirazione in 021. Questi dati avevano guidato la scrittura di S2, quindi li ho usati solo come controllo.

**Test su 40 note nuove.**

| Variante | A | P | E | U | Popup |
|---|---:|---:|---:|---:|---:|
| S1 | 23 | 7 | 9 | 1 | 22 |
| S2-V | 24 | 7 | 8 | 1 | 21 |
| S2-R | 23 | 7 | 9 | 1 | 22 |
| S2-VR | 24 | 7 | 8 | 1 | 21 |

Le quattro varianti danno lo stesso output su 39/40 note. L'unica differenza è UC01-S2TEST-019, «Magari un giorno imparerò a suonare il violoncello»: S1 e S2-R lo propongono, S2-V e S2-VR no, come previsto dal gold.

Dopo il test ho fissato la policy sul caso 029, «Non è necessario comprare la batteria; va invece controllato il caricatore.»: un obbligo impersonale concreto e ancora da svolgere va proposto, sempre come suggerimento da confermare. Nessuna variante lo propone, quindi diventa E per tutte: S1 e S2-R 23 A / 7 P / 10 E, S2-V e S2-VR 24 A / 7 P / 9 E. L'esito assoluto cambia, la graduatoria no. Questa decisione è post-hoc e non preregistrata.

Gli errori comuni a tutte le varianti sono la parte più interessante:

- omissioni (004, 005, 011, 028, 029): per esempio in 028, «Non devo stampare i biglietti, ma domani devo scaricare il QR code.», S1 estende la negazione anche alla seconda frase e la scarta;
- falsi popup su azioni di terzi (013 «La segreteria sta aspettando una risposta dal corriere», 014 «Il vicino deve sistemare il cancello del cortile») e su intenzioni vaghe che S2-V non intercetta (021, 024);
- popup pertinenti ma incompleti, senza scadenza o contesto (001, 006, 031, 032, 033, 036, 037);
- in 030 ci sono tre azioni e se ne propone una, per il vincolo di un popup per nota.

## Cosa ne concludo

S1 ha fatto quello per cui l'avevo pensato sulle 24 note di sviluppo, ma su quelle note l'avevo anche progettato. Sull'holdout di 32 note la candidata X0+C2+Z+S1 non si è dimostrata superiore alla baseline: due miglioramenti netti, due regressioni e un pareggio complessivo nei popup.

Sul test di 40 note ho scelto **S2-V** come selettore candidato: elimina un falso popup in più di S1 senza peggioramenti osservati. S2-R non porta vantaggi e S2-VR ottiene lo stesso risultato di S2-V con un intervento in più. La configurazione candidata di ricerca diventa quindi X0+C2+Z+S2-V; X0+C2+Z+S1 resta il riferimento riproducibile e X0+C0+Z+S0 la baseline storica, che però non è stata rieseguita sulle 40 note. Non ho modificato il prototipo.

I limiti sono importanti. Il guadagno di S2-V è un solo caso su 40. Tutte le note sono sintetiche; i giudizi A/P/E/U vengono da una revisione preliminare assistita, con un gold ancora da confermare e una policy (029) decisa dopo aver visto i risultati. Non è una validazione indipendente e non dice nulla sulla superiorità statistica. Le regole di S2 sono euristiche linguistiche e potrebbero bloccare un impegno reale scritto in modo insolito. Il set da 40 note ormai è noto: non lo userò per ottimizzare nuove regole. Molti errori residui dipendono da X0 e da C2 più che dal selettore, e per questo il passo successivo è stato l'analisi dell'estrazione.

## Dati

`04-selettori-dati.csv`: una riga per nota e configurazione (272 righe). `prova` indica la sottoprova (`dev24_S0_vs_S1`, `holdout32_S0_vs_S1`, `test40_S1_S2`); `configurazione` la pipeline usata; `popup_atteso` il gold (SI/NO/DA_VALUTARE, vuoto per le 24 di sviluppo); `popup` e `testo_popup` cosa è stato proposto; `esito` il giudizio A/P/E/U (A corretto, P parziale, E errato o mancante, U da decidere secondo policy; vuoto per le 24 di sviluppo, dove c'è solo il commento); `esito_prima_policy_029` il giudizio del test40 prima della policy sul caso 029; `motivazione` e `causa_principale` il commento di revisione e il componente a cui è attribuito l'errore (X0, C2, Z, S).
