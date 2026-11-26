# 09 — Ripetibilità di C2-CTX su input identici

## Da dove nasce l'idea

Nel confronto tra I1 e I1-R (esperimento 08) una delle quattro azioni cambiate, la 011-a1 («Sabato pomeriggio è fissata la prova dell'orchestra»), aveva un input identico nelle due condizioni. Eppure `completion` era passato da PENDING a DONE e `uncertain` da True a False. Se il classificatore può cambiare risposta senza che cambi nulla in ingresso, non posso attribuire con sicurezza alla revisione del contesto nemmeno le altre differenze.

Prima di progettare un nuovo classificatore volevo quindi sapere quanto C2-CTX v01 sia stabile quando riceve esattamente la stessa richiesta più volte.

## Cosa ho fatto

- **Azioni:** 20 in tutto. Sono le 18 azioni con contesto revisionato in I1-R, più due controlli con input invariato: la 011-a1, dove avevo visto la discrepanza, e la 002-a1 («Stasera ricordarmi di rinnovare la tessera della biblioteca»).
- **Input:** I1-R congelato. Per ogni azione le tre richieste hanno lo stesso hash dell'input.
- **Ripetizioni:** 3 round per azione, quindi 60 inferenze. L'ordine è diretto nel primo round, inverso nel secondo e di nuovo diretto nel terzo, così round e posizione di esecuzione non coincidono del tutto.
- **Modello e parametri:** Qwen3-1.7B con llama.cpp, stesso prompt e schema di C2-CTX v01, `temperature=0`, `seed=42`, `max_tokens=350`, contesto 4096, `ngl=0` (solo CPU), 6 thread.
- **Misura:** per ogni azione controllo se le sei uscite (`kind`, `intent`, `subject_owner`, `polarity`, `completion`, `uncertain`) sono identiche in tutti e tre i round. Non è un test di accuratezza. Z e S2-V non sono stati eseguiti.

## Cosa si vede

- **60/60** risposte ricevute e valide rispetto allo schema.
- **19/20** azioni identiche in tutti e sei i campi nei tre round.
- Una sola azione instabile, la **026-a1** («Ho disdetto la visita, quindi non devo andare in ambulatorio lunedì»): `intent` è COMPLETED nel round 1 e 3 e COMMITTED nel round 2, mentre `completion` resta DONE in tutti e tre.
- Nessuna variazione in `kind`, `subject_owner`, `polarity`, `completion` e `uncertain`.

| Campo | Azioni con valori diversi tra i round |
|---|---:|
| kind | 0 |
| intent | 1 |
| subject_owner | 0 |
| polarity | 0 |
| completion | 0 |
| uncertain | 0 |

La 026-a1 è proprio l'azione per cui nell'esperimento 08 avevo considerato un «miglioramento plausibile» il passaggio da COMMITTED a COMPLETED con I1-R. Alla luce di questo test quel miglioramento è meno solido di come lo avevo letto.

Il controllo 011-a1, invece, qui è stabile: TASK/COMMITTED/SELF/POSITIVE/PENDING con `uncertain=True` in tutti e tre i round, come nella condizione I1 dell'esperimento 08. Il valore DONE visto con I1-R non si è ripresentato.

Le risposte stabili però sono spesso sbagliate, e sempre nello stesso modo:

- `subject_owner=SELF` in tutte le 60 risposte;
- «La visita con l'oculista è confermata per venerdì alle 15:30» (008) è TASK/COMMITTED con `completion=DONE`, tutte e tre le volte;
- il fornitore di 017 è sempre SELF;
- «Mi piacerebbe aprire un laboratorio di ceramica, prima o poi» (020) è sempre TASK/COMMITTED;
- «Non devo più ritirare il pacco: ci pensa già Alessia» (025) è sempre TASK/COMMITTED/SELF/DONE;
- la citazione del romanzo (038) è sempre un TASK personale.

## Cosa ne concludo

La variabilità su input identici è limitata ma non nulla: un'azione su venti ha cambiato `intent`. È abbastanza per non leggere ogni singola differenza nei confronti precedenti come effetto della modifica, ma non spiega gli errori principali. Il problema di C2-CTX v01 sembra soprattutto la **correttezza semantica**, non l'instabilità: il modello ripete la stessa risposta sbagliata in modo coerente. Una risposta ripetuta non è per questo una risposta giusta.

La configurazione candidata resta `X0 → C2 → Z → S2-V`.

Il passo successivo è progettare **C2-CTX v02** come nuovo classificatore sperimentale, con uno schema più semplice e meno campi. L'idea, ancora solo abbozzata, è separare tre decisioni: la natura dell'elemento (TASK, EVENT, FACT, dove un appuntamento confermato non è un task), chi parla o chi deve agire (SELF, THIRD_PARTY, QUOTED, UNCLEAR, così una citazione non diventa un impegno personale) e lo stato dell'azione (ACTIONABLE, TENTATIVE, NEGATED, DONE, INFORMATIONAL, UNCLEAR). Prima di provarlo dovrò congelare prompt, esempi e criteri di valutazione, poi fare un confronto diagnostico sulle note già note e, solo dopo, valutarlo su note nuove.

Limiti: il test è piccolo (20 azioni, 3 ripetizioni) e usa note sintetiche già utilizzate nello sviluppo. Misura la stabilità delle risposte, non la loro correttezza, e non dice nulla sui popup. Non posso nemmeno dire quale fattore tecnico causi la variazione osservata.

## Dati

`09-ripetibilita-c2ctx-dati.csv` ha 20 righe, una per azione. `gruppo` distingue le 18 azioni `revisionata` (contesto I1-R) dai 2 `controllo`; `nota` e `azione` sono il testo; `ripetizioni` e `valide` contano le risposte; `identico_tutte_le_volte` vale 1 se le sei uscite coincidono nei tre round e `configurazioni_distinte` conta le combinazioni diverse ottenute. Le colonne `kind`, `intent`, `subject_owner`, `polarity`, `completion` e `uncertain` riportano il valore ottenuto; quando cambia tra i round compaiono i tre valori in ordine (round 1 / 2 / 3). `campi_variabili` elenca i campi instabili, `ordine_r1_r2_r3` la posizione dell'azione in ciascun round e `latenza_ms_r1_r2_r3` i tempi di risposta.
