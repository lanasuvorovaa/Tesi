# Piano di lavoro

Questo file descrive dove voglio arrivare con la tesi e i passaggi che ho in programma da qui alla consegna. Lo aggiorno man mano che le fasi si chiudono.

## Dove voglio arrivare

L'obiettivo finale è un'**applicazione mobile**, per ora **per Android** (e in seguito, se c'è tempo, anche per iPhone), in cui scrivo una nota in linguaggio naturale e un modello linguistico piccolo, eseguito sul telefono, la interpreta e, quando ha senso, propone di trasformarla in un'attività o in un appuntamento. Il modello non agisce mai da solo: interpreta il testo, una parte deterministica verifica le condizioni e decide se proporre, chiedere un chiarimento o non intervenire, e l'ultima parola spetta sempre all'utente.

I casi d'uso previsti sono tre:

| Caso d'uso | Cosa fa | Stato attuale |
|---|---|---|
| **UC-01** — Note, attività ed eventi | Estrae TASK / EVENT / FACT da una nota, ne classifica l'intenzione (COMMITTED, TENTATIVE, HYPOTHETICAL, COMPLETED, NEGATED, INFORMATIONAL) e decide tra PROPOSE, CLARIFY, NO_ACTION | Pipeline X0 → C2 → Z → S2-V sperimentata su Mac (esperimenti 01–09) e prototipo funzionante |
| **UC-02** — Relazioni tra informazioni | Riconosce collegamenti tra attività, persone e progetti (appartenenza, destinatario, «prima di») | Solo progettato |
| **UC-03** — Domande sui dati personali | Risponde a domande sull'archivio («Quali attività ho ancora aperte per il progetto Loto?») usando solo i dati memorizzati | Solo progettato |

I vincoli principali sono l'elaborazione locale (privacy), tempi di risposta e consumo di memoria compatibili con uno smartphone, la tracciabilità delle decisioni e la separazione tra dati di sviluppo e dati di valutazione.

Con circa **due mesi** a disposizione (consegna indicativa: fine gennaio 2027), la priorità è portare UC-01 a un livello valutato in modo onesto e farlo funzionare in un'app Android reale, con un piccolo test con utenti. UC-02 e UC-03 li affronto in forma ridotta, come prova di fattibilità, così da poter discutere nella tesi cosa funziona e cosa no, senza pretendere di completarli.

## Le fasi

Legenda: **[essenziale]** = deve esserci nella tesi; **[se c'è tempo]** = lo faccio solo se le fasi essenziali sono in linea con il calendario.

### Fase 1 — Chiudere UC-01 dal lato del modello [essenziale]
*Settimane 1–2 (30 novembre – 13 dicembre)*

Finora ho lavorato su note sintetiche che conoscevo già. Prima di tutto mi serve una valutazione su note nuove.

1. **Preparare un set di valutazione nuovo**: circa 60 note scritte da 3–4 persone diverse da me, con poche istruzioni («scrivi appunti come li scriveresti per te»). Le note non verranno usate per modificare prompt o regole.
2. **Scrivere il gold prima di eseguire la pipeline**: per ogni nota, il comportamento atteso (PROPOSE / CLARIFY / NO_ACTION) e, se c'è, l'attività attesa. Un secondo annotatore etichetta in modo indipendente almeno 20 note, per misurare quanto siamo d'accordo.
3. **C2-CTX v02, con tempo limitato (massimo una settimana)**: schema di output più semplice e regole esplicite per eventi/task, soggetto, citazioni, desideri e negazioni. Lo provo prima sulle note già note e, solo se migliora davvero, sul set nuovo.
4. **Valutazione finale di UC-01** sul set nuovo, con la configurazione candidata (X0 → C2 → Z → S2-V) ed eventualmente con C2-CTX v02.
5. Ricontrollare il giudizio sulla nota 019 dell'esperimento 06.

Cosa misuro: esiti A/P/E per nota, falsi popup (proposte su note che non ne richiedevano), opportunità perse, CLARIFY appropriati, accordo tra annotatori, tempo per nota.

Quando la considero chiusa: ho i risultati sul set nuovo e ho deciso quale classificatore va nell'app. **Se C2-CTX v02 non è chiaramente migliore, resta C2** e non insisto oltre.

### Fase 2 — Il modello gira sul telefono? Scelta della tecnologia [essenziale]
*Settimane 2–3 (7 – 20 dicembre)*

Per ora sviluppo **solo per Android**. Uso però **React Native** con la libreria **llama.rn**, che porta llama.cpp (lo stesso motore che uso sul Mac) dentro l'app: è un framework multipiattaforma, quindi se più avanti vorrò una versione per iPhone potrò riusare gran parte del codice. Strumenti: VS Code per il codice, Android Studio per l'SDK e l'emulatore. Se llama.rn dovesse dare problemi, l'alternativa è Flutter.

1. Creare un'app di prova che carica Qwen3-1.7B Q4 e analizza una nota, su **almeno un telefono Android reale** (l'emulatore va bene per l'interfaccia, ma è troppo lento per misurare il modello).
2. Misurare, con le stesse note della Fase 1: tempo per nota, memoria massima occupata, consumo di batteria su una serie di 50 note.
3. Se i tempi non sono accettabili, provare un modello più piccolo (per esempio Qwen3-0.6B) o una quantizzazione più spinta, e misurare quanta qualità si perde.
4. Riscrivere la parte deterministica della pipeline (Z e S2-V, oggi in Python) nel linguaggio del framework, verificando con gli stessi casi di test che dia gli stessi risultati della versione Python.

Quando la considero chiusa: llama.rn funziona sul telefono, so quale modello e quale quantizzazione usare e ho una tabella Mac contro Android.

### Fase 3 — Applicazione Android minima [essenziale]
*Settimane 3–5 (14 dicembre – 10 gennaio, con la pausa delle feste)*

Funzioni:
- inserimento della nota;
- analisi in locale con la pipeline UC-01;
- popup con proposta, richiesta di chiarimento oppure nessun intervento;
- conferma, modifica o rifiuto da parte dell'utente: niente viene salvato senza conferma;
- archivio locale (SQLite) di note, attività ed eventi, con un controllo semplice sui duplicati;
- registro delle decisioni (cosa ha estratto il modello, perché il sistema ha proposto o no), per la tracciabilità;
- un pulsante per lasciare un **commento** su ogni proposta («utile», «sbagliata», «mancava qualcosa» e testo libero), che mi serve per il test con utenti.

Quando la considero chiusa: l'app funziona offline su un telefono Android reale, dall'inserimento della nota alla conferma.

### Fase 4 — UC-02 e UC-03 in forma ridotta [essenziale in forma minima]
*Settimane 5–6 (4 – 17 gennaio)*

- **UC-02:** solo relazioni dentro la stessa nota (attività → progetto, attività → persona destinataria, attività A prima di attività B). Prova diagnostica su circa 30 note, misurando relazioni corrette, mancanti e inventate. Nell'app le relazioni vengono mostrate e confermate, non applicate in automatico.
- **UC-03:** il modello non risponde «a memoria». Trasforma la domanda in un filtro strutturato (tipo di elemento, persona, progetto, stato, intervallo di date), che l'app esegue sull'archivio. Prova su circa 20 domande con un archivio di prova noto, misurando risposte corrette, incomplete e inventate, e verificando che il sistema dica «non ho trovato nulla» quando è così.

### Fase 5 — Test con utenti [essenziale]
*Settimane 6–7 (11 – 24 gennaio)*

1. 5–8 persone con un telefono Android usano l'app per circa una settimana con le proprie note.
2. Raccolgo i commenti lasciati sulle proposte e un breve questionario finale (utilità, fastidio dei suggerimenti, fiducia).
3. Le note restano sul telefono: raccolgo solo i commenti e le statistiche (numero di proposte accettate, rifiutate, modificate), anonimizzati e con il consenso delle persone.

### Fase 6 — Scrittura e chiusura [essenziale]
*In parallelo da subito, poi a tempo pieno nelle settimane 7–9 (fino a fine gennaio)*

- I capitoli su obiettivi, requisiti e casi d'uso sono già in bozza.
- Il capitolo sugli esperimenti lo scrivo a dicembre, partendo dai file in `esperimenti/`.
- Le ultime due settimane sono per i risultati delle Fasi 1–5, le conclusioni e la revisione con il relatore.

### Versione per iPhone [se c'è tempo]

Se l'app Android funziona e il calendario lo permette, provo a compilare lo stesso progetto React Native per iOS e a ripetere le misure su un iPhone reale. Cosa serve:

- **Xcode** sul Mac (gratuito, dall'App Store);
- un iPhone su cui fare le prove;
- per far provare l'app sugli iPhone di altre persone (TestFlight), un **account Apple Developer** a pagamento. Con l'account gratuito posso installarla solo sui miei dispositivi, e l'installazione scade dopo pochi giorni.

### Esperimento facoltativo — Analisi di file [se c'è tempo]

All'inizio mi piaceva l'idea di far analizzare all'assistente anche dei documenti (per esempio un PDF con delle scadenze). Un modello di queste dimensioni non legge direttamente un file e fa fatica con testi lunghi, ma il problema si può aggirare:

1. il testo viene estratto dal codice dell'app, non dal modello (PDF digitali e documenti di testo);
2. il documento viene diviso in pezzi brevi e ogni pezzo passa nella pipeline UC-01 come se fosse una nota;
3. le proposte vengono raccolte e mostrate con il riferimento al punto del documento da cui vengono.

I documenti scansionati e le foto richiederebbero un riconoscimento del testo (OCR) e li lascio fuori. Se c'è tempo, faccio una prova su circa 10 documenti brevi, misurando scadenze e attività trovate, mancanti e inventate, oltre al tempo per documento. In ogni caso, nella tesi lo presenterei come sviluppo futuro con una prima verifica di fattibilità.

## Calendario indicativo

| Settimana | Periodo | Fase |
|---|---|---|
| 1 | 30 nov – 6 dic | Fase 1: set nuovo e gold; C2-CTX v02 |
| 2 | 7 – 13 dic | Fase 1: valutazione UC-01 · Fase 2: app di prova su Android con llama.rn |
| 3 | 14 – 20 dic | Fase 2: misure sui telefoni · Fase 3: avvio app |
| 4 | 21 dic – 3 gen | Fase 3: app (ritmo ridotto per le feste) · capitolo esperimenti |
| 5 | 4 – 10 gen | Fase 3: chiusura app · Fase 4: UC-02 |
| 6 | 11 – 17 gen | Fase 4: UC-03 · Fase 5: inizio test con utenti |
| 7 | 18 – 24 gen | Fase 5: test in corso, analisi dei commenti · scrittura |
| 8–9 | 25 gen – fine gen | Scrittura, revisione con il relatore, consegna |

Se la Fase 1 o la Fase 2 si allungano, rinuncio per prima cosa alla versione per iPhone e all'esperimento sui file, poi riduco UC-03 a pochi tipi di domanda. La Fase 5 e la scrittura non le comprimo.

## Cosa mi serve per partire

- Le **note del set nuovo**, scritte da persone diverse da me (Fase 1).
- Un **secondo annotatore** per circa 20 note (Fase 1).
- Almeno un **telefono Android** su cui fare le misure, possibilmente anche uno di fascia media (Fase 2).
- Le **persone disponibili per il test** dell'app, a gennaio (Fase 5).
- Per l'esperimento facoltativo, una decina di **documenti brevi**, non personali o anonimizzati.
