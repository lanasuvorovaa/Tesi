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

Ho tempo fino a **fine febbraio 2027**, cioè circa tre mesi. La priorità è portare UC-01 a un livello valutato in modo onesto e farlo funzionare in un'app Android reale, con un piccolo test con utenti. UC-02 e UC-03 li affronto in forma ridotta, come prova di fattibilità, così da poter discutere nella tesi cosa funziona e cosa no, senza pretendere di completarli.

## Cosa può fare l'app quando l'utente accetta una proposta

Capire bene la nota non basta: bisogna anche decidere **quali azioni l'app sa davvero eseguire**, perché una proposta ha senso solo se, dopo il «sì», l'app è in grado di portarla a termine.

### Chi fa cosa

Il modello e l'app hanno ruoli separati:

1. **Il modello interpreta**: individua l'attività o l'evento, la classifica e propone *quale* azione potrebbe servire (per esempio «creare un evento»), con i dati che trova nella nota.
2. **L'app verifica**: la parte deterministica (Z) controlla che l'azione sia tra quelle disponibili e autorizzate dall'utente e che ci siano tutti i dati necessari. Se manca qualcosa, per esempio la data di un appuntamento, chiede un chiarimento invece di proporre.
3. **L'utente decide**: vede la proposta, la può modificare, accettare o rifiutare.
4. **L'app esegue**: dopo la conferma, l'azione viene eseguita da codice normale, senza il modello. Il codice controlla e normalizza i campi (date, orari, titolo), chiama la funzione del telefono o l'API corrispondente e registra l'esito.

In questo modo un errore del modello può al massimo produrre una proposta sbagliata, che l'utente rifiuta. Non può mai produrre un'azione eseguita per sbaglio.

### Le azioni previste

Per ogni azione devo stabilire se rientra nella tesi e come si collega al telefono. Il prototipo ha già un registro delle azioni (`capability_registry.json`) con lo stato di ciascuna, da aggiornare nell'app.

| Azione | Come la esegue l'app | Cosa serve all'utente | Nella tesi |
|---|---|---|---|
| Creare un'attività o un promemoria | Salvataggio nell'archivio locale dell'app, con notifica alla scadenza | Nulla | Essenziale |
| Creare un evento nel calendario | L'app apre il calendario del telefono con l'evento già compilato (titolo, data, ora, persone) e l'utente lo salva lì | Nulla, il calendario del telefono è già collegato al suo account | Essenziale |
| Controllare il calendario prima di proporre (sovrapposizioni, eventi già presenti) | Lettura del calendario unificato (vedi «Plugin») | Permesso di lettura del calendario | Se c'è tempo |
| Programmare una call | Come un evento. Il link di Meet, Teams o Zoom lo crea il plugin del servizio, se collegato | Collegare il plugin del servizio | Solo evento. Link automatico se c'è tempo |
| Preparare un messaggio o una mail | Il modello scrive una bozza. L'app apre l'app di posta o di messaggistica con il testo precompilato. L'app non invia mai da sola | Nulla | Se c'è tempo |
| Fare un piccolo piano (scomporre un'attività in passi, ordinare attività collegate) | Proposta di più attività collegate (si lega a UC-02) | Nulla | Sviluppo futuro |
| Inviare messaggi, fare acquisti, agire per conto dell'utente verso terzi | — | — | Escluso |

Le azioni che richiedono di collegare un account esterno (Google, Microsoft, Zoom) passano dai plugin descritti qui sotto: l'utente li attiva solo se vuole e l'app deve funzionare anche senza.

### Plugin: collegare servizi esterni

Tutto ciò che viene da fuori dall'app (Google, Microsoft, Zoom e altri) lo tratto come un **plugin**: un modulo che l'utente collega solo quando vuole attivare una certa funzione e che può scollegare in qualsiasi momento. Ogni plugin dichiara:

- quali dati legge e cosa può fare (per esempio «legge gli eventi», «crea eventi», «crea il link di una riunione»),
- quale permesso chiede all'utente (permesso del telefono oppure accesso all'account del servizio),
- cosa succede quando lo scollego: i dati importati da quel servizio vengono cancellati dall'app.

Le azioni dei plugin entrano nel registro delle azioni: un'azione può essere proposta solo se il plugin che la esegue è collegato. Il collegamento e l'esecuzione sono gestiti da codice normale, non dal modello. I dati restano sul telefono, le credenziali sono salvate in modo protetto e il modello riceve solo le informazioni che servono per la singola proposta.

**Il calendario unificato.** L'app ha un proprio calendario che unisce gli appuntamenti delle diverse fonti, senza AI, con un algoritmo:

- mostra insieme gli eventi di tutte le fonti collegate, ciascuno con l'indicazione della provenienza,
- se due eventi si sovrappongono, lo segnala con una nota («alle 10 hai già un appuntamento su Teams»),
- se lo stesso appuntamento compare in due calendari (stesso titolo, stessa ora), lo mostra una volta sola indicando le due fonti,
- un pulsante permette di nascondere gli eventi di una fonte (per esempio tutti quelli di Google).

Il primo passo è semplice: su Android, i calendari Google, Outlook ed Exchange aggiunti agli account del telefono sono già leggibili dal calendario del telefono, con un solo permesso. In questo modo il calendario unificato funziona senza collegare nessuna API esterna. I plugin con accesso diretto all'account servono per le cose in più, come creare il link di una riunione.

**Plugin possibili**, tutti con API pubbliche e con il consenso dell'utente:

| Plugin | Cosa permette | Come si collega | Priorità |
|---|---|---|---|
| Calendario del telefono | Leggere gli eventi di tutti i calendari già presenti sul telefono (Google, Outlook, Samsung…) e creare eventi | Permesso Android, nessun account da collegare | Prima, è la base del calendario unificato |
| Contatti del telefono | Riconoscere le persone citate nelle note («Giada», «Luca») e collegarle a eventi e attività (aiuta UC-02) | Permesso Android | Se c'è tempo |
| Google Calendar | Leggere e creare eventi direttamente sull'account, creare il link di Google Meet | Accesso all'account Google (OAuth) | Se c'è tempo, come primo plugin con accesso diretto |
| Microsoft (Outlook e Teams) | Eventi del calendario Outlook, creazione di riunioni Teams | Accesso all'account Microsoft (OAuth, Microsoft Graph) | Sviluppo futuro |
| Zoom | Creare il link di una riunione Zoom da mettere nell'evento | Accesso all'account Zoom (OAuth) | Sviluppo futuro |
| Google Tasks / Microsoft To Do | Sincronizzare le attività create dall'app con le liste che l'utente usa già | Accesso all'account (OAuth) | Sviluppo futuro |
| File (Google Drive, OneDrive, file del telefono) | Scegliere un documento da caricare per le domande sui documenti | Selettore di file di Android, senza accesso all'account | Insieme alla prova sui documenti |
| Posta (Gmail, Outlook) | Preparare bozze di mail o trovare appuntamenti nelle mail | Accesso all'account, con permessi molto delicati | Sviluppo futuro |

Una nota pratica: per i plugin con accesso all'account (Google, Microsoft, Zoom) bisogna registrare l'app presso il servizio. Per una tesi basta la modalità di prova, che permette l'accesso a un numero limitato di utenti indicati a mano, sufficiente per me e per chi fa il test. Per la posta i permessi sono considerati particolarmente sensibili, per questo la lascio come sviluppo futuro.

### Non essere invadente

Un assistente che a ogni frase manda una proposta diventa fastidioso anche quando ha ragione. Per questo, oltre alla correttezza, controllo **quanto spesso** l'app interviene:

- al massimo **una proposta per nota**, mostrata dentro l'app quando salvo la nota, non come notifica push,
- **nessuna proposta** per desideri generici, ipotesi, azioni già fatte o negate e azioni di altre persone,
- una proposta **rifiutata non viene riproposta** per la stessa nota,
- se rifiuto più volte di fila lo stesso tipo di proposta, l'app diventa più prudente per quel tipo,
- un'impostazione per scegliere quanto essere proattiva: «solo cose esplicite», «normale», «spenta».

Nei test misuro quindi anche: falsi positivi (proposte su note che non ne richiedevano), proposte ogni 10 note, percentuale di proposte accettate, modificate e rifiutate e, nel test con utenti, quanto le persone le hanno trovate fastidiose.

## Le fasi future

### Fase 1 — Chiudere UC-01 dal lato del modello [essenziale]
*30 novembre – 13 dicembre*

Finora ho lavorato su note sintetiche che conoscevo già. Prima di tutto mi serve una valutazione su note nuove.

1. **Preparare un set di valutazione nuovo**: circa 60 note scritte da 3–4 persone diverse da me, con poche istruzioni («scrivi appunti come li scriveresti per te»). Le note non verranno usate per modificare prompt o regole.
2. **Scrivere il gold prima di eseguire la pipeline**: per ogni nota, il comportamento atteso (PROPOSE / CLARIFY / NO_ACTION) e, se c'è, l'attività attesa. Un secondo annotatore etichetta in modo indipendente almeno 20 note, per misurare quanto siamo d'accordo.
3. **C2-CTX v02 [se c'è tempo]**, con tempo limitato (massimo una settimana), da fare solo mentre aspetto le note degli altri: schema di output più semplice e regole esplicite per eventi/task, soggetto, citazioni, desideri e negazioni. Lo provo prima sulle note già note e, solo se migliora davvero, sul set nuovo.
4. **Valutazione finale di UC-01** sul set nuovo, con la configurazione candidata (X0 → C2 → Z → S2-V) ed eventualmente con C2-CTX v02.
5. Ricontrollare il giudizio sulla nota 019 dell'esperimento 06.

Cosa misuro: esiti A/P/E per nota, falsi popup (proposte su note che non ne richiedevano), opportunità perse, CLARIFY appropriati, accordo tra annotatori, tempo per nota.

Quando la considero chiusa: ho i risultati sul set nuovo e ho deciso quale classificatore va nell'app. **Se C2-CTX v02 non è chiaramente migliore, resta C2** e non insisto oltre.

### Fase 2 — Il modello gira sul telefono? Scelta della tecnologia [essenziale]
*7 – 20 dicembre*

Per ora sviluppo **solo per Android**. Uso però **React Native** con la libreria **llama.rn**, che porta llama.cpp (lo stesso motore che uso sul Mac) dentro l'app: è un framework multipiattaforma, quindi se più avanti vorrò una versione per iPhone potrò riusare gran parte del codice. Strumenti: VS Code per il codice, Android Studio per l'SDK e l'emulatore. Se llama.rn dovesse dare problemi, l'alternativa è Flutter.

1. Creare un'app di prova che carica Qwen3-1.7B Q4 e analizza una nota, su **almeno un telefono Android reale** (l'emulatore va bene per l'interfaccia, ma è troppo lento per misurare il modello).
2. Misurare, con le stesse note della Fase 1: tempo per nota, memoria massima occupata, consumo di batteria su una serie di 50 note.
3. Solo se i tempi non sono accettabili, provare un modello più piccolo (per esempio Qwen3-0.6B) o una quantizzazione più spinta, e misurare quanta qualità si perde.
4. Riscrivere la parte deterministica della pipeline (Z e S2-V, oggi in Python) nel linguaggio del framework, verificando con gli stessi casi di test che dia gli stessi risultati della versione Python.

Quando la considero chiusa: llama.rn funziona sul telefono, so quale modello e quale quantizzazione usare e ho una tabella Mac contro Android.

### Fase 3 — Applicazione Android minima [essenziale]
*17 dicembre – 17 gennaio, con la pausa delle feste*

Funzioni:
- inserimento della nota,
- analisi in locale con la pipeline UC-01,
- popup con proposta, richiesta di chiarimento oppure nessun intervento,
- conferma, modifica o rifiuto da parte dell'utente: niente viene salvato senza conferma,
- archivio locale (SQLite) di note, attività ed eventi, con un controllo semplice sui duplicati,
- registro delle decisioni (cosa ha estratto il modello, perché il sistema ha proposto o no), per la tracciabilità,
- esecuzione delle azioni dopo la conferma: attività nell'archivio interno ed evento nel calendario del telefono, gestita da codice deterministico e non dal modello,
- le regole per non essere invadente descritte sopra (una proposta per nota, niente riproposte dopo un rifiuto, livello di proattività regolabile),
- un pulsante per lasciare un **commento** su ogni proposta («utile», «sbagliata», «mancava qualcosa» e testo libero), che mi serve per il test con utenti.

Quando la considero chiusa: l'app funziona offline su un telefono Android reale, dall'inserimento della nota alla conferma.

### Fase 4 — UC-02 e UC-03 in forma ridotta [essenziale in forma minima]
*18 – 31 gennaio*

- **UC-02:** solo relazioni dentro la stessa nota (attività → progetto, attività → persona destinataria, attività A prima di attività B). Prova diagnostica su circa 20 note, misurando relazioni corrette, mancanti e inventate. Nell'app le relazioni vengono mostrate e confermate, non applicate in automatico.
- **UC-03:** il modello non risponde «a memoria». Trasforma la domanda in un filtro strutturato (tipo di elemento, persona, progetto, stato, intervallo di date), che l'app esegue sull'archivio. Prova su circa 15 domande con un archivio di prova noto, misurando risposte corrette, incomplete e inventate, e verificando che il sistema dica «non ho trovato nulla» quando è così.

### Fase 5 — Test con utenti [essenziale]
*12 – 29 gennaio (preparazione, una settimana di uso, analisi)*

1. 5–8 persone con un telefono Android usano l'app per circa una settimana con le proprie note.
2. Raccolgo i commenti lasciati sulle proposte e un breve questionario finale (utilità, fastidio dei suggerimenti, fiducia).
3. Le note restano sul telefono: raccolgo solo i commenti e le statistiche (numero di proposte accettate, rifiutate, modificate), anonimizzati e con il consenso delle persone.

### Fase 6 — Scrittura del testo finale (circa 60 pagine) [essenziale]
*In parallelo da subito, a tempo pieno a febbraio*

La scrittura procede in parallelo allo sviluppo da dicembre e diventa l'attività principale a febbraio, quando sviluppo e test sono chiusi. L'ultima settimana di febbraio è dedicata alla revisione con il relatore, alle correzioni e alla consegna.

### Versione per iPhone [se c'è tempo]

Se l'app Android funziona e il calendario lo permette, provo a compilare lo stesso progetto React Native per iOS e a ripetere le misure su un iPhone reale. Cosa serve:

- **Xcode** sul Mac (gratuito, dall'App Store),
- un iPhone su cui fare le prove,
- per far provare l'app sugli iPhone di altre persone (TestFlight), un **account Apple Developer** a pagamento. Con l'account gratuito posso installarla solo sui miei dispositivi, e l'installazione scade dopo pochi giorni.

### Domande sui documenti caricati [se c'è tempo, priorità alta]

L'idea che mi interessa di più è questa: carico un documento sul telefono (un PDF, un contratto, un regolamento, una bolletta) e poi faccio domande sul suo contenuto, per esempio «Entro quando devo dare la disdetta?» o «Quanto costa il canone mensile?». L'assistente risponde **solo con quello che c'è scritto nel documento**, indica da quale pagina ha preso la risposta e dice chiaramente quando l'informazione non c'è. Tutto resta in locale, perché si tratta di documenti personali.

È lo stesso principio di UC-03 (rispondere solo con i dati memorizzati), applicato ai documenti invece che all'archivio delle note.

**Un modello piccolo ce la fa?** Non se gli si dà tutto il documento in una volta: un testo lungo occupa troppa memoria sul telefono, rallenta molto la risposta e un modello da 1–2 miliardi di parametri perde facilmente il filo. La strada più usata in questi casi è far lavorare il modello solo sui pezzi utili:

1. **estrazione del testo**: la fa il codice dell'app, non il modello (PDF digitali e documenti di testo). Per scansioni e foto serve un riconoscimento del testo (OCR), che su Android esiste anche offline: lo aggiungo solo se la prova sui PDF digitali va bene,
2. **divisione in pezzi** di qualche paragrafo, ciascuno con il numero di pagina,
3. **ricerca dei pezzi pertinenti**: per ogni domanda l'app trova i 2–3 pezzi più vicini, prima con una semplice ricerca per parole chiave e poi, se serve, con un piccolo modello di "embedding" che confronta il significato delle frasi e gira anch'esso in locale,
4. **risposta**: il modello riceve la domanda e solo quei pezzi, risponde citando la pagina oppure dice «non lo trovo nel documento».

Mi aspetto che funzioni abbastanza bene per domande dirette, con la risposta scritta in una frase del documento, e peggio per domande che richiedono di mettere insieme parti diverse, per le tabelle e per i documenti molto lunghi. Il rischio principale è che il modello **inventi** una risposta quando il documento non la contiene: è la prima cosa da misurare.

**La prova.** La faccio prima sul Mac, con lo stesso llama.cpp degli esperimenti, perché è molto più veloce da preparare che sul telefono:

- 8–10 documenti brevi, non personali o anonimizzati,
- circa 40 domande scritte prima di eseguire la prova, di tre tipi: risposta diretta, risposta che richiede di unire due punti del documento, domanda la cui risposta non c'è,
- cosa misuro: risposte corrette, parziali, sbagliate e inventate, quante volte il modello dice giustamente «non lo trovo», se la ricerca ha trovato il pezzo giusto, tempo per domanda,
- se c'è tempo, confronto Qwen3-1.7B con un modello un po' più grande (per esempio Qwen3-4B), per capire quanto conta la dimensione del modello in questo compito.

Se i risultati sono buoni, la porto nell'app Android. Se non lo sono, nella tesi diventa comunque un risultato utile: dove arriva e dove si ferma un modello piccolo su questo compito.

## Calendario

Riepilogo dei passaggi già affrontati e di quelli previsti fino alla consegna del 28 febbraio 2027. Aggiornato al 26 novembre 2026.

### Svolto — settembre / novembre 2026

| Periodo | Attività / risultato | Stato |
|---|---|---|
| 21–30 set 2026* | Definizione del problema e dei casi d'uso UC-01, UC-02 e UC-03 | Concluso |
| 1–10 ott 2026* | Prime prove su note sintetiche e criteri di valutazione | Concluso |
| 7–27 ott 2026* | Prima pipeline X/C/Z/S e prototipo locale su Mac | Concluso |
| 28 ott – 9 nov 2026* | Ricerca e confronto tra Qwen3-1.7B, Qwen3.5-2B e LFM2.5-1.2B | Concluso |
| 7–22 nov 2026* | Classificatori C0/C1/C2 e selettori S0/S1/S2 | Concluso |
| 19–24 nov 2026* | Estrazione X0/X1/X2 e valutazione delle azioni atomiche | Concluso |
| 24–25 nov 2026 | Confronto P0/P1: citazione atomica e contesto | Concluso |
| 25 nov 2026 | Interfaccia I1 e confronto C2/C2-CTX v01 | Concluso |
| 25 nov 2026 | Audit I1, correzioni I1-R e confronto delle classificazioni | Concluso |
| 25 nov 2026 | Test di ripetibilità: 60 inferenze su 20 azioni | Concluso |
| 26 nov 2026 | Aggiornamento del prototipo Mac con X0 → C2 → Z → S2-V | Versione di prova |
| 26 nov 2026 | Organizzazione di README, documentazione e file per GitHub | Concluso |

### Programmato — novembre 2026 / febbraio 2027

| Periodo | Attività / risultato | Stato |
|---|---|---|
| 30 nov – 13 dic 2026 | UC-01: raccolta di circa 60 note nuove, gold, secondo annotatore e valutazione finale (M1: classificatore scelto) | Da fare |
| 7 – 20 dic 2026 | Prova di inferenza su Android e misure di tempi, memoria e batteria (M2: modello scelto) | Da fare |
| 17 dic 2026 – 17 gen 2027 | App Android minima: note, suggerimenti, conferma, archivio locale, eventi nel calendario del telefono (M3: app pronta) | Da fare |
| 12 – 29 gen 2027 | Preparazione, utilizzo e analisi del test con 5–8 utenti | Da fare |
| 18 – 31 gen 2027 | UC-02 e UC-03: prove di fattibilità in forma ridotta | Da fare |
| 30 nov 2026 – 21 feb 2027 | Scrittura della tesi in parallelo. Attività principale a febbraio | Da fare |
| 21 – 28 feb 2027 | Revisione con il relatore, correzioni e consegna | Da fare |
| Febbraio 2027, facoltativo | Domande sui documenti caricati, calendario unificato e primi plugin, eventuale versione iOS | Solo se c'è tempo |

\* Date indicative: gli intervalli segnati con l'asterisco sono ricostruzioni a posteriori, non date di esecuzione verificate né giorni effettivamente lavorati. Le date senza asterisco corrispondono a quelle dei report degli esperimenti. Le fasi possono sovrapporsi. Le attività future sono pianificate e possono essere aggiornate.

## Elenco dei task

Le stime sono in giorni di lavoro effettivo. I task in corsivo sono facoltativi o condizionati. Diverse attività si sovrappongono nel calendario perché alcune aspettano qualcosa (le note dagli altri, il secondo annotatore, i tester) e nel frattempo vado avanti con altro.

| ID | Task | Stima | Dipende da | Risultato |
|---|---|---:|---|---|
| T1.1 | Scrivere le istruzioni e raccogliere 60 note da 3–4 persone | 2 (+ attesa) | — | `dati/set_valutazione.csv` |
| T1.2 | Scrivere il gold per ogni nota e congelare il protocollo | 3 | T1.1 | Gold e protocollo |
| T1.3 | Secondo annotatore su 20 note, calcolo dell'accordo | 1 (+ attesa) | T1.2 | Tabella di accordo |
| *T1.4* | *C2-CTX v02, solo se c'è tempo mentre aspetto le note (massimo 7 giorni)* | *5* | — | *Esperimento 10* |
| T1.5 | Eseguire la pipeline sul set nuovo (C2 ed eventualmente v02) | 1 | T1.2 | Output grezzi |
| T1.6 | Revisione degli esiti, metriche, decisione sul classificatore | 3 | T1.5 | Esperimento 11, M1 |
| T1.7 | Ricontrollare la nota 019 dell'esperimento 06 | 0,5 | — | Correzione esperimento 06 |
| T2.1 | Installare Node, React Native e Android SDK. App vuota sul telefono | 2 | — | Progetto `app/` |
| T2.2 | Integrare llama.rn, caricare Qwen3-1.7B e analizzare una nota | 3 | T2.1 | Prima nota analizzata sul telefono |
| T2.3 | Misurare tempi, memoria e batteria su 50 note | 2 | T2.2 | Tabella Mac contro Android |
| *T2.4* | *Solo se i tempi non vanno bene: modello più piccolo o altra quantizzazione* | *2* | T2.3 | Scelta del modello, M2 |
| T2.5 | Riscrivere Z e S2-V in TypeScript e confrontarli con la versione Python | 4 | T2.1 | Test di equivalenza |
| T3.1 | Struttura dell'app e schermata di inserimento delle note | 3 | T2.1 | |
| T3.2 | Pipeline UC-01 completa nell'app | 5 | T2.2, T2.5, M1 | |
| T3.3 | Popup di proposta e chiarimento. Conferma, modifica, rifiuto | 4 | T3.2 | |
| T3.4 | Archivio locale SQLite e controllo dei duplicati | 3 | T3.3 | |
| T3.5 | Registro delle decisioni e commenti sulle proposte | 2 | T3.3 | |
| T3.7 | Esecuzione delle azioni confermate: attività nell'archivio, evento nel calendario del telefono | 1 | T3.4 | |
| T3.8 | Regole anti-invadenza e livello di proattività regolabile | 1 | T3.3 | |
| T3.6 | Test completo offline e preparazione dell'APK | 2 | T3.4, T3.5, T3.7, T3.8 | APK, M3 |
| T4.1 | UC-02: prompt per le relazioni, 20 note con gold | 3 | M1 | |
| T4.2 | UC-02: valutazione e visualizzazione delle relazioni nell'app | 2 | T4.1, T3.4 | Esperimento 12 |
| T4.3 | UC-03: domanda → filtro strutturato, archivio di prova, 15 domande | 3 | T3.4 | |
| T4.4 | UC-03: valutazione | 1 | T4.3 | Esperimento 13 |
| T5.1 | Modulo di consenso, questionario, istruzioni per i tester | 1 | — | |
| T5.2 | Distribuire l'APK. Una settimana di uso | 1 (+ attesa) | M3, T5.1 | Commenti e statistiche |
| T5.3 | Analisi dei commenti e del questionario | 2 | T5.2 | Esperimento 14 |
| W1 | Scrittura del testo finale (circa 60 pagine), in parallelo alle altre fasi | 31 | — | |
| W2 | Revisione con il relatore, correzioni, impaginazione e consegna | 4 | W1 | Consegna |
| *F1* | *Versione per iPhone (facoltativo)* | *5* | *M3* | |
| *F2* | *Domande sui documenti: prova sul Mac con 8–10 documenti e circa 40 domande (facoltativo, priorità alta)* | *4* | *M1* | |
| *F2b* | *Domande sui documenti nell'app Android, se la prova sul Mac va bene (facoltativo)* | *4* | *F2, M3* | |
| *F3* | *Bozze di messaggi o mail precompilate (facoltativo)* | *3* | *M3* | |
| *F4* | *Calendario unificato con il plugin del calendario del telefono: unione delle fonti, segnalazione delle sovrapposizioni, eventi doppi, nascondi per fonte (facoltativo)* | *3* | *T3.7* | |
| *F5* | *Primo plugin con accesso all'account: Google Calendar con link Meet (facoltativo)* | *3* | *F4* | |
| *F6* | *Plugin dei contatti del telefono per riconoscere le persone (facoltativo)* | *2* | *T3.4* | |

## Il piano sta nei tempi?

Dal 30 novembre al 28 febbraio, lavorando sei giorni a settimana e togliendo le feste, ho circa **75 giorni di lavoro**.

- Il piano iniziale completo ne richiedeva circa **98**: non ci stava.
- Il piano descritto qui, con C2-CTX v02 e il modello alternativo resi facoltativi e UC-02/UC-03 un po' ridotti, ne richiede circa **90** (55 tra sviluppo, esperimenti e test, 35 di scrittura).

Mancano quindi ancora circa due settimane. Le stime sono indicative e le ricalibro dopo M1, quando saprò quanto vado veloce davvero. Se il ritardo si conferma, taglio in questo ordine, senza comprimere la scrittura:

1. task facoltativi (iPhone, domande sui documenti, bozze di messaggi, calendario unificato e plugin, C2-CTX v02): restano fuori finché non c'è margine. Se si libera tempo, il primo da recuperare è la prova sui documenti,
2. UC-02 e UC-03 solo progettati, con una dimostrazione su pochi casi e senza valutazione completa (circa −5 giorni),
3. test con utenti più leggero, 3–5 persone per pochi giorni (circa −2),
4. app senza controllo dei duplicati e con commenti più semplici (circa −3).

Con tutti questi tagli il piano scende a circa **80 giorni**, a ridosso del tempo disponibile. M1 (13 dicembre), M2 (20 dicembre) e M3 (17 gennaio) sono i punti in cui controllo se sono in linea.

## Cosa mi serve per partire

- Le **note del set nuovo**, scritte da persone diverse da me (Fase 1).
- Un **secondo annotatore** per circa 20 note (Fase 1).
- Almeno un **telefono Android** su cui fare le misure, possibilmente anche uno di fascia media (Fase 2).
- Le **persone disponibili per il test** dell'app, nella seconda metà di gennaio (Fase 5).
- Per la prova sui documenti, 8–10 **documenti brevi** non personali o anonimizzati (contratti tipo, regolamenti, bollette di esempio) e le **domande** da fare su ciascuno, scritte prima della prova.
