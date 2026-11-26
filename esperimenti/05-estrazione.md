# 05 — Estrazione: X0, X1 e X2

## Da dove nasce l'idea

Chiudendo il lavoro sui selettori mi sono accorta che molti errori residui non dipendevano da S. Ho ripreso le 40 tracce del test S2 (estrazione grezza, citazioni validate, C2, Z, selezione) e ho fatto una diagnosi nota per nota. Il problema più frequente era a monte, nell'estrazione X0:

- X0 spezza la frase e separa l'azione dai suoi vincoli: in 001 «Devo spedire il campione al laboratorio» resta senza «entro lunedì mattina», in 011 «è fissata la prova dell'orchestra» perde «Sabato pomeriggio»;
- in alcune note (005, 031) la citazione prodotta dal modello non è letterale e il validatore la respinge;
- in 036 e 037 il frammento scelto contiene un pronome («Quello firmato», «ci passo») che si capisce solo leggendo la frase precedente.

Altri errori (004 e 028 per il selettore, 013, 014, 021, 024, 029 per il classificatore) li ho lasciati fuori: in questa prova volevo cambiare una sola cosa, l'estrazione, tenendo fissi C2, Z e S2-V.

## Cosa ho fatto

Tutte le prove usano le stesse 40 note sintetiche del test S2, quindi note già conosciute: sono prove diagnostiche, non una validazione. Il modello è sempre Qwen3-1.7B (Q4) in locale con llama.cpp, con gli stessi parametri deterministici delle prove precedenti. C2, Z e S2-V sono verificati tramite hash e restano invariati; resta il limite di un popup per nota. Per il giudizio uso il gold delle 40 note con la policy chiusa dopo il test S2 (caso 029 proponibile).

1. **X0 contro X1.** Cambia solo il testo del prompt di estrazione. X1 chiede segmenti autosufficienti che tengano insieme, se contigui, verbo, oggetto, destinatario, luogo e scadenza, senza però fondere attività diverse. La prima esecuzione di X1 si era bloccata perché il trasporto accettava solo il prompt X0 registrato; ho aggiunto un adattatore che sostituisce solo il messaggio di sistema, lasciando uguali temperatura, seed, schema e chiamata.
2. **X2 v01.** Un'estrazione "atomica": il modello restituisce un JSON con le singole azioni (`action_quote`), gli elementi di contesto con il loro ruolo (tempo, luogo, destinatario, negazione...), le relazioni tra azioni e gli intervalli di caratteri di ogni citazione. A C2 e Z arriva comunque solo `action_quote`. Qui non cambia solo il prompt ma anche lo schema e la validazione.
3. **X2 v02.** Stesso schema, ma il modello non deve più calcolare le posizioni: gli intervalli li ricava Python cercando la citazione esatta e univoca nella nota, senza correzioni approssimate.

## Cosa si vede

**X0 contro X1.**

| | X0 | X1 |
|---|---:|---:|
| Frammenti validati | 55 | 37 |
| Popup | 21 | 18 |
| Chiamate al modello | 95 | 77 |
| Tempo logico medio per nota | 3,149 s | 2,456 s |
| A / P / E | 24 / 7 / 9 | 25 / 5 / 10 |

I testi dei popup cambiano in 10 note (in 024 solo per la punteggiatura). X1 migliora 001 e 006, dove la scadenza resta nel popup («Devo caricare il documento firmato sul portale entro le 18.»), e 021, dove non propone più «Forse cambierò città». Però peggiora 033 (il task sparisce) e 035 (la citazione viene invalidata e il task si perde). In 030 passa da un task valido, «Per il viaggio devo pesare la valigia», a un popup che unisce tre attività in una frase: più completo come testo, meno corretto come unità da proporre. In 031 e 032 recupera contesto ma fonde due azioni.

**X2 v01.** Il modello ha prodotto 66 azioni grezze su 40 note: 61 citazioni erano presenti alla lettera nella nota, 5 no, ma nessuno dei 66 intervalli numerici era corretto. Per esempio in 001 cita «spedire» indicando la posizione [10, 14], e inventa una seconda azione «inviare» che nella nota non c'è. Risultato: 0 frammenti validati e 0 popup. Questo zero non è un filtro migliore: semplicemente nessun candidato arrivava a C2. Riapplicando offline l'allineatore di v02 a queste stesse risposte (senza nuove inferenze), le azioni accettate sarebbero 44 su 66.

**X2 v02.** Tutte le 40 note arrivano in fondo alla pipeline. Su 55 azioni grezze ne vengono accettate 39 e rifiutate 16; i popup sono 17.

| Esito per nota | X0 | X1 | X2 v02 |
|---|---:|---:|---:|
| A | 24 | 25 | 16 |
| P | 7 | 5 | 11 |
| E | 9 | 10 | 13 |

Le azioni diventano più atomiche, ma a C2 arriva un pezzo troppo corto. In 001 e 006 il popup è solo «spedire» o «caricare». In 008 resta «La visita con l'oculista è confermata» senza venerdì e 15:30. In altre note manca proprio la proposta (002, 012, 034, 036, 037) e compaiono falsi popup su azioni di terzi o aspirazioni: «invii» in 017 (obbligo contrattuale del fornitore), «imparerò a suonare il violoncello» in 019. X2 recupera qualcosa che X0 perdeva, la telefonata all'assicurazione in 004 e la restituzione del trapano in 005, ma senza giorno né scopo. Il tempo logico totale è stato 492,3 s, contro 191,1 s di X0 nella stessa esecuzione.

## Cosa ne concludo

Non ho sostituito X0. X1 conserva meglio scadenze e luoghi ma, allungando le citazioni, unisce azioni diverse e in qualche caso perde il task; il bilancio (25 A contro 24) è troppo piccolo e non a senso unico. X2 v01 mi ha insegnato che un modello così piccolo non riesce a calcolare le posizioni dei caratteri; v02 risolve questo problema tecnico, ma la qualità per nota peggiora (16 A contro 24).

La cosa più utile che ho capito è che il punto critico non è solo l'estrazione, ma l'interfaccia verso il classificatore: se a C2 passa soltanto l'azione breve, negazioni, scadenze e soggetto vanno persi, anche quando X2 li aveva estratti nel contesto. Per questo il passo successivo non poteva essere "un altro prompt di estrazione", ma una prova separata su cosa passare a C2 (esperimento 06). La configurazione candidata resta X0+C2+Z+S2-V.

Limiti: le 40 note sono sintetiche e già usate per progettare i selettori e queste varianti; i giudizi A/P/E vengono da una revisione preliminare assistita, ancora da confermare con un annotatore umano; il gold del caso 029 è stato fissato dopo il test S2. I tempi valgono solo per il mio Mac. Nessuno di questi numeri è una validazione indipendente.

## Dati

`05-estrazione-dati.csv`: una riga per nota e variante (160 righe). `prova` indica la sottoprova (`x0_vs_x1`, `x2_v01`, `x2_v02`; le righe X0 e X1 rieseguite insieme a X2 v02 avevano gli stessi popup e le ho omesse); `gold_popup_atteso` e `gold_azione_attesa` vengono dal gold con policy chiusa; `frammenti_validati` sono le citazioni passate a C2; `popup_testo`, `tipo_popup`, `intenzione_popup` descrivono la proposta; `esito` è il giudizio A/P/E (A corretto o corretta assenza di popup, P pertinente ma incompleto, E errato o mancante; vuoto per X2 v01, che non produceva candidati); `falso_popup` e `opportunita_persa` sono compilati solo per X2 v02; le colonne `x2_*` riportano azioni grezze, accettate ed errori del validatore; `chiamate_modello` e `tempo_logico_ms` il costo per nota.
