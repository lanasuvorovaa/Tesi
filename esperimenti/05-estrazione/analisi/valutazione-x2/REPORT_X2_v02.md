# UC-01 — Revisione diagnostica X2 v02

## Stato della prova

- Esecuzione completa: 40 note × 3 varianti = 120 righe. Tutte le 40 esecuzioni X2 producono un risultato di pipeline senza eccezioni bloccanti.
- Dataset diagnostico riutilizzato: **non** è un holdout indipendente e non deve essere impiegato come dimostrazione di generalizzazione.
- X2 v02 risolve il blocco degli offset: il matching degli span è deterministico e non richiede al modello di calcolare indici numerici.
- Le citazioni, anche quando validate, non attestano correttezza semantica: il popup usa esclusivamente `action_quote`, mentre i metadati di contesto non sono passati a C2/Z/S2-V.

## Conteggi tecnici

| Metrica | X0 | X1 | X2 v02 |
|---|---:|---:|---:|
| Frammenti validati | 55 | 37 | 39 |
| Popup prodotti | 21 | 18 | 17 |

X2: **55** azioni grezze; **39** azioni accettate; **16** azioni rifiutate; **66** elementi di contesto grezzi. Un’azione accettata non è necessariamente un popup.

## Revisione qualitativa (provvisoria)

| Esito per nota | X0 | X1 | X2 v02 |
|---|---:|---:|---:|
| Corretto/autonomo o no-popup corretto | 24 | 25 | 16 |
| Pertinente ma incompleto | 7 | 5 | 11 |
| Errato/omesso | 9 | 10 | 13 |

La lettura A/P/E di X0 e X1 riprende la valutazione qualitativa precedente, verificando che popup e testi coincidano con questa esecuzione. La lettura X2 è nuova ed è assistita: richiede convalida umana prima dell’uso come risultato definitivo.

## Casi decisivi

- **001, 006:** X2 propone il verbo isolato (“spedire”, “caricare”) invece di un’attività completa; pur avendo estratto dati contestuali, non li porta al popup.
- **002, 011, 012, 034, 036, 037:** X2 non propone attività/eventi che il gold richiede.
- **004 e 005:** X2 recupera una telefonata e la restituzione del trapano che X0 non proponeva; perde però dettagli temporali e/o finalità.
- **013, 017, 019, 024:** X2 genera falsi popup su attività di terzi, obblighi contrattuali e aspirazioni.
- **030, 033:** X2 isola attività diverse, ma il limite di un popup per nota rimane; 033 perde il riferimento a sabato.
- **028, 029:** restano le omissioni di azioni positive in contesto misto/impersonale.

## Variazioni qualitative rispetto a X0

| Caso | X0 | X2 | Diagnosi |
|---|---|---|---|
| 002 | A | E | Omissione di promemoria esplicito; citazione accettata ma nessun popup. |
| 003 | A | P | Azione riconosciuta, ma il vincolo «prima della riunione» non compare nel popup. |
| 004 | E | P | Telefonata riconosciuta, ma mancano mercoledì e lo scopo «chiedere la nuova polizza». |
| 005 | E | P | Recupera un’attività che X0 perdeva; il popup omette sabato. |
| 007 | A | P | Azione e destinataria presenti, ma manca domattina. |
| 008 | A | P | Evento riconosciuto, ma perde venerdì e 15:30. |
| 009 | A | P | Solo «colloquio online»: manca la cooperativa e l’orario. |
| 012 | A | E | Non propone la consulenza fiscale prenotata. |
| 014 | E | A | Nessun popup su obbligo del vicino. |
| 017 | A | E | Falso popup «invii»: obbligo contrattuale del fornitore. |
| 019 | A | E | Falso popup su aspirazione futura non impegnativa. |
| 021 | E | A | Nessun popup sulla possibilità di trasloco non decisa. |
| 032 | P | E | Nessun popup per le due azioni operative. |
| 034 | A | E | Omissione dell’incontro confermato alla biblioteca. |
| 035 | A | P | Rivedere le slide è corretto, ma mancano Elena e mercoledì. |
| 036 | P | E | Nessuna proposta per consegnare il modulo firmato venerdì. |
| 037 | P | E | Nessuna proposta per ritirare le casse lunedì. |

## Decisione

**Non promuovere X2 v02** come sostituto di X0. Risolve la validazione degli indici e separa alcune azioni multiple, ma la proiezione atomica priva di contesto causa numerose regressioni e falsi popup. Mantenere come configurazione candidata `X0+C2+Z+S2-V`.

## Prossimo esperimento, solo dopo nuova specifica

Non basta reiterare il prompt: occorre progettare l’interfaccia X→C2 per trasferire in modo sicuro azione, soggetto, negazione locale, modalità e vincoli temporali senza fabbricare citazioni. Poiché il contratto di input e il flusso a valle potrebbero cambiare, tale intervento **non** può essere descritto come “solo estrazione modificata”: va preregistrato come esperimento di interfaccia/ricomposizione separato.

## Provenienza e limiti

- Fonte primaria: ZIP `x0_x1_x2_20261124_233634.zip` (manifest, due CSV e 120 dettagli per nota/variante).
- Gold: `gold_test40_POLICY_CHIUSA_POST_TEST.csv`; la decisione sul caso 029 è successiva al primo run e resta esplicitamente post-test.
- Risultati X0/X1 confrontati con il precedente `revisione_80_esiti.csv`; nessuna differenza nel testo o nella presenza dei popup rispetto al CSV presente nel nuovo ZIP.
- Tutte le valutazioni qualitative sono assistite e da confermare con annotatore umano; campione sintetico piccolo e già noto.
