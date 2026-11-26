# 06 — Quanto contesto passare al classificatore: P0 contro P1

## Da dove nasce l'idea

Con X2 v02 (esperimento 05) l'estrazione atomica funzionava dal punto di vista tecnico, ma la qualità dei popup era peggiorata rispetto a X0: 16 note corrette contro 24. Guardando i casi mi sono accorta che spesso il problema non era l'azione estratta, ma quello che arrivava al classificatore. X2 aveva trovato anche il contesto (scadenze, luoghi, negazioni), però a C2 passava solo la citazione breve: in 001 il popup era «spedire», mentre «entro lunedì mattina» restava nei metadati e non veniva usato.

La domanda quindi era: se, a parità di azioni estratte, passo a C2 una porzione più ampia della nota, le proposte diventano più complete senza introdurre nuovi errori?

## Cosa ho fatto

Non ho rieseguito l'estrazione. Ho riusato le azioni X2 già accettate nell'esecuzione del 24 novembre (39 azioni sulle stesse 40 note sintetiche) e ho cambiato solo la proiezione, cioè il testo che entra nel validatore e poi in C2, Z e S2-V:

- **P0 (atomica):** passa soltanto la `action_quote` già validata, come in X2 v02,
- **P1 (clausola):** passa un pezzo contiguo della nota originale che contiene l'azione, delimitato da punteggiatura, contrasti e, quando riconosciute, dalle altre azioni X2. Toglie solo un eventuale connettore avversativo iniziale. Non unisce frammenti lontani, non aggiunge parole o date e non corregge citazioni.

C2, Z e S2-V sono copie congelate controllate con hash. Il modello (Qwen3-1.7B Q4 in locale con llama.cpp) viene chiamato solo per C2, con gli stessi parametri deterministici. Prima dell'esecuzione ho fatto un controllo offline della costruzione delle citazioni: in 28 note su 40 P1 è diversa da P0, e tutte le citazioni sono sottostringhe esatte della nota. Il gold non è stato letto dalla pipeline. L'ho usato solo nella revisione, nella versione con la policy chiusa dopo il test S2 (caso 029 proponibile).

Va detto che non è un esperimento che cambia solo X: l'input di C2 cambia di proposito, e di conseguenza anche Z e il selettore vedono citazioni diverse, pur con codice invariato.

## Cosa si vede

Entrambe le varianti hanno 39 citazioni validate e producono 18 popup, ma non sulle stesse note (i popup cambiano in 002, 004, 017, 019, 021 e 032).

| Esito per nota | P0 atomica | P1 clausola |
|---|---:|---:|
| A — corretto e autonomo, o corretta assenza di popup | 16 | 25 |
| P — pertinente ma incompleto | 12 | 4 |
| E — falso popup o attività omessa | 12 | 11 |

Il giudizio cambia in 13 note e resta uguale nelle altre 27. Il guadagno riguarda soprattutto la completezza delle proposte:

- in 001, 003, 005, 006, 007, 009, 034 e 035 P1 recupera scadenze, oggetti e destinatari. Per esempio «caricare» diventa «Devo caricare il documento firmato sul portale entro le 18» e «colloquio online» diventa «Lunedì alle nove c'è il colloquio online con la cooperativa»,
- in 002 P0 non proponeva il task esplicito, P1 sì («Stasera ricordarmi di rinnovare la tessera della biblioteca»),
- in 017 P0 proponeva «invii» come task mio, mentre con la frase intera («Il contratto prevede che il fornitore invii...») non c'è più popup.

Ci sono però due regressioni importanti:

- **004:** P0 proponeva la telefonata, anche se incompleta. Con la citazione lunga «Mercoledì telefono all'assicurazione per chiedere la nuova polizza» il selettore applica il veto `TEMPORAL_ONLY` e non propone nulla, nonostante C2 la classifichi TASK/COMMITTED,
- **021:** P1 isola «Forse cambierò città» dalla seconda parte «per ora non ho deciso nulla» e la propone, mentre P0 correttamente non proponeva niente.

Altri problemi restano uguali con entrambe: azioni di terzi (013, «La segreteria sta aspettando una risposta dal corriere»), aspirazioni vaghe (024, «Sarebbe bello partecipare a una maratona un giorno», proposta anche se C2 la classifica TENTATIVE), l'azione positiva esclusa per la negazione vicina in 028, l'omissione di 029, gli eventi confermati non proposti (011, 012) e le azioni che X2 non aveva estratto (036, 037). In 031 e 032 P1 mette due attività nello stesso popup: più completo non vuol dire più atomico.

## Cosa ne concludo

Dare più contesto al classificatore rende le proposte spesso più complete (25 A contro 16), ma da solo non basta: può far perdere un'attività reale (004) o far comparire un falso popup (021), e non risolve negazioni, soggetti terzi e desideri vaghi. Allungare la citazione non è un'interfaccia robusta tra X2 e C2.

Non ho promosso P1 e la configurazione candidata resta X0+C2+Z+S2-V. L'idea che porto avanti è un'interfaccia che tenga **separati** l'azione atomica (come candidato) e il contesto (clausola, modificatori, riferimenti verificati nel testo), invece di allungare sempre le citazioni. Questo però cambia l'input di C2, quindi va trattato come un nuovo esperimento sull'interfaccia e sul classificatore, non come "C2 invariato".

Limiti: le 40 note sono sintetiche e le conoscevo già prima di progettare P1, quindi è una prova diagnostica di sviluppo e non una validazione indipendente. I giudizi A/P/E vengono da una revisione preliminare assistita, ancora da confermare. La policy sul caso 029 è stata decisa dopo il test S2. La proiezione per clausole è un'euristica, non un'analisi grammaticale. Nella revisione la nota 019 risulta E anche per P1, ma nei dati P1 non mostra alcun popup (il candidato viene escluso da S2-V): è un giudizio che devo ricontrollare. Infine P0 dovrebbe riprodurre X2 v02 e lo fa su 39 note su 40: l'unica differenza è 034, dove P0 propone «è confermato» e X2 v02 non proponeva nulla.

## Dati

`06-contesto-p0-p1-dati.csv`: una riga per nota e variante (80 righe). `variante` è `P0_ATOMICA` o `P1_CLAUSOLA`. `gold_popup_atteso` viene dal gold con policy chiusa. `azioni_x2` sono le azioni X2 congelate e `citazioni_passate_a_C2` il testo effettivamente passato al classificatore. `citazioni_modificate` quante citazioni P1 ha allargato rispetto a P0 (sempre 0 per P0). `popup`, `decisione` (tipo e intenzione assegnati da C2, oppure NO_POPUP) e `testo_popup` descrivono la proposta. `esito` è il giudizio A/P/E (A corretto o corretta assenza di popup, P pertinente ma incompleto, E falso popup o attività omessa) con la sua `motivazione`.
