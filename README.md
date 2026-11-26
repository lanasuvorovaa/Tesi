# Assistente AI locale per la gestione delle note

Questo repository raccoglie il prototipo e gli esperimenti che sto svolgendo per la mia tesi. L'obiettivo è costruire un assistente che lavori in locale, interpreti note scritte in linguaggio naturale e **proponga** attività o appuntamenti pertinenti, senza effettuare modifiche automatiche senza conferma.

Il prodotto finale a cui voglio arrivare è un'**applicazione mobile**, per ora per Android (e in seguito, se c'è tempo, anche per iPhone), che esegue un modello linguistico piccolo direttamente sul telefono e copre tre casi d'uso: riconoscere attività, eventi e informazioni nelle note (**UC-01**), collegarle tra loro (**UC-02**) e rispondere a domande sui dati memorizzati (**UC-03**). Il lavoro fatto finora riguarda soprattutto UC-01. Obiettivi, fasi e calendario fino alla consegna sono descritti in [`PIANO_DI_LAVORO.md`](PIANO_DI_LAVORO.md).

Il README racconta soprattutto **quali prove ho fatto e perché sono passata da una all'altra**. Il dettaglio di ogni esperimento e i relativi dati sono nella cartella [`esperimenti/`](esperimenti/).

## Il percorso in breve

All'inizio ho preparato note di prova per capire se un piccolo modello linguistico fosse in grado di riconoscere attività, eventi e informazioni che non devono diventare promemoria. Mi sono accorta che non bastava trovare un verbo: il sistema doveva distinguere, per esempio, una cosa da fare da un desiderio, una citazione o un'azione che spetta a un'altra persona.

Con quello che avevo imparato da queste prime prove ho costruito un **primo prototipo** sul Mac, collegando estrazione, classificazione, controlli e selezione delle proposte, con Qwen3-1.7B in locale tramite llama.cpp. Usandolo ho capito che funzionava, ma che andava modificato e migliorato in più punti.

Prima di intervenire ho approfondito come vengono usati in pratica gli small language model: ho cercato materiale online e non solo, per capire come altre persone li provano e li adattano a compiti simili, quali modelli usano e con quali accorgimenti. Da qui sono nati il confronto tra modelli alternativi e una serie di test mirati sui singoli componenti della pipeline.

Sulla base di questi risultati ho sviluppato una **nuova versione del prototipo**, che usa la configurazione emersa dagli esperimenti ed è quella presente nella cartella [`prototipo/`](prototipo/).

## I test svolti, in ordine

### 1. Prime prove sulle note e definizione dei casi

- **Cosa volevo capire:** se il modello riconoscesse task, eventi, date, negazioni e contenuti da ignorare.
- **Cosa ho fatto:** ho costruito note sintetiche e raccolto esempi di errori. In seguito ho usato un development set di 24 note, altri set diagnostici e un insieme sintetico di 40 note.
- **Cosa ho imparato:** dovevo valutare non solo se compariva un popup, ma anche se fosse corretto, completo e attribuito alla persona giusta.

### 2. Primo prototipo locale

- **Cosa volevo ottenere:** passare dai singoli test a una demo con componenti collegati.
- **Cosa ho fatto:** ho organizzato la pipeline in **X (estrazione) → C (classificazione) → Z (controlli) → S (selezione)** e l'ho fatta lavorare con Qwen3-1.7B sul Mac.
- **Cosa ho imparato:** il prototipo andava migliorato, e un errore nel risultato finale può dipendere da componenti diversi. Per capirne la causa servono test separati.

### 3. Approfondimento sugli small language model e confronto tra modelli

- **Modelli considerati:** Qwen3-1.7B, Qwen3.5-2B e LFM2.5-1.2B.
- **Cosa volevo capire:** come vengono usati in pratica i modelli piccoli e se fosse meglio sostituire il modello di riferimento invece di continuare a cambiare prompt e regole.
- **Cosa ho fatto:** ho raccolto informazioni su come altre persone usano e provano questi modelli, ho scelto alcune alternative e ho confrontato risultati e comportamento sul mio scenario.
- **Decisione:** ho mantenuto **Qwen3-1.7B** come modello di riferimento per le prove successive. Questo non significa che sia universalmente il modello migliore, ma che è rimasto la scelta di lavoro per il prototipo.

### 4. Classificazione: C0 contro C1

- **Cosa ho cambiato:** il prompt di classificazione, mantenendo 45 frammenti di estrazione condivisi.
- **Risultato sulle 24 note di sviluppo:** classificazioni corrette per entrambi i campi (`kind` e `intent`) da **17/45 a 18/45**.
- **Decisione:** il miglioramento era troppo piccolo e accompagnato da regressioni. Ho continuato a lavorare sul classificatore.

### 5. Classificazione: C0 contro C2

- **Cosa ho cambiato:** una nuova versione del prompt C, senza modificare gli altri componenti del confronto.
- **Risultato sugli stessi 45 frammenti:** da **17/45 a 22/45** classificazioni corrette per entrambi i campi, ma con **5 regressioni** su risultati prima corretti.
- **Decisione:** non ho sostituito subito C0 nella pipeline stabile, ma C2 è diventato il classificatore candidato per le prove successive, pur con errori ancora presenti su negazioni, contesti e contenuti citati.

### 6. Selettore delle proposte: S0 contro S1

- **Cosa volevo risolvere:** evitare popup prodotti da frammenti che, isolati, sembravano azioni ma non lo erano.
- **Risultato sulle 24 note di sviluppo:** da **14 a 12 popup**. Sono stati eliminati **2 falsi popup noti**, senza perdere proposte valide precedentemente selezionate in quel set.
- **Decisione:** continuare con S1 e provarlo su altre note. Su un holdout di 32 note nuove la combinazione X0+C2+Z+S1 non è risultata migliore della baseline X0+C0+Z+S0 (18 corretti, 6 parziali, 6 errati contro 18, 5, 7, più 2 casi non decidibili per entrambe, due miglioramenti e due regressioni).

### 7. Selettori S1, S2-V, S2-R e S2-VR

- **Cosa ho fatto:** ho confrontato quattro varianti del selettore su **40 nuove note sintetiche**.
- **Risultato:** S2-V e S2-VR hanno evitato il falso popup su «Magari un giorno imparerò a suonare il violoncello». Le quattro varianti davano lo stesso esito su **39/40 note**.
- **Decisione:** mantenere **S2-V** come selettore candidato, senza confondere il vantaggio su un caso con una validazione generale.

### 8. Estrazione delle informazioni: X0 contro X1

- **Cosa volevo migliorare:** conservare informazioni importanti come date, oggetti e destinatari nelle citazioni estratte.
- **Risultato sulle 40 note note:** X1 recuperava alcuni dettagli, ma peggiorava altri casi e univa azioni separate. Valutazione qualitativa **X0: 24 corretti, 7 parziali, 9 errati. X1: 25 corretti, 5 parziali, 10 errati**.
- **Decisione:** non sostituire X0.

### 9. Estrazione atomica: X2 v01 e X2 v02

- **Cosa volevo risolvere:** distinguere più azioni nella stessa nota, mantenendo il relativo contesto.
- **X2 v01:** il modello individuava citazioni utili, ma non produceva intervalli testuali affidabili. Gli offset sono stati poi ricostruiti con un allineamento esatto in Python.
- **X2 v02:** su 40 note sono state accettate **39 azioni**. La valutazione finale per nota era **16 corretti, 11 parziali, 13 errati**, peggiore della pipeline X0 sui casi osservati.
- **Decisione:** non adottare X2. Il punto critico era anche l'interfaccia: passare al classificatore solo l'azione breve faceva perdere negazioni e scadenze.

### 10. Proiezione delle citazioni: P0 contro P1

- **Cosa ho confrontato:** **P0**, che passa la sola azione atomica, e **P1**, che passa una clausola più estesa della nota.
- **Risultato su 40 note:** P0 **16 corretti / 12 parziali / 12 errati**. P1 **25 corretti / 4 parziali / 11 errati**. Entrambe generavano 18 popup, ma non sugli stessi casi.
- **Cosa ho imparato:** più contesto rende spesso le proposte più complete, ma può introdurre falsi popup o far perdere attività reali.
- **Decisione:** progettare un'interfaccia che mantenga **azione e contesto separati**, invece di allungare sempre le citazioni.

### 11. Prima interfaccia contestuale: I1 e C2-CTX v01

- **Cosa ho provato:** passare al classificatore l'azione atomica con riferimenti al contesto. Ho confrontato **C2 e C2-CTX** sulle stesse **39 azioni**, ottenendo **78 classificazioni valide**.
- **Risultato:** i due classificatori differivano su **16/39 azioni**. C2-CTX recuperava alcuni task, ma confondeva molti eventi con task e attribuiva **SELF a tutte le 39 azioni**, anche quando riguardavano terzi o citazioni.
- **Decisione:** non adottare C2-CTX v01.

### 12. Audit dei dati inviati al classificatore

- **Cosa volevo capire:** se gli errori dipendessero dal modello o da contesti già rappresentati male.
- **Risultato:** nei **50 riferimenti contestuali** trasferiti a I1, la revisione preliminare ha rilevato **29 ruoli incoerenti** e **5 riferimenti troppo ampi**. Inoltre non erano state trasferite relazioni tra attività.
- **Decisione:** correggere prima i dati di ingresso e confrontarli con la versione originale.

### 13. Revisione del contesto: I1 contro I1-R

- **Cosa ho cambiato:** i contesti di **18 azioni** appartenenti a 12 note, lasciando invariate le **39 azioni X2** e C2-CTX v01.
- **Risultato:** **35/39 classificazioni identiche** nei sei campi analizzati. Solo quattro azioni hanno avuto almeno una differenza. Non è migliorata la distinzione tra eventi e task né l'attribuzione del soggetto.
- **Decisione:** correggere i dati, da solo, non basta. Un cambiamento è comparso perfino a input invariato, quindi serviva un test di ripetibilità.

### 14. Ripetibilità di C2-CTX su input identici

- **Cosa ho fatto:** **20 azioni**, ripetute **3 volte** ciascuna con stessi input e parametri: **60 inferenze**.
- **Risultato:** **60/60 risposte valide**, **19/20 azioni stabili** in tutti i campi. Una sola azione oscillava nell'intenzione tra `COMPLETED` e `COMMITTED`.
- **Cosa ho imparato:** il problema principale sembra essere la **correttezza semantica**, più che la variabilità delle risposte. Una risposta ripetuta può comunque essere sbagliata.

## Dove sono arrivata

La configurazione **candidata**, che non ho sostituito con le varianti sperimentali meno affidabili, è:

**`X0 → C2 → Z → S2-V`**

È la configurazione usata nella nuova versione del prototipo, che si trova in [`prototipo/`](prototipo/) insieme a un breve video dimostrativo.

I prossimi passi, in breve:

1. valutare UC-01 su un **set di note nuove**, scritte da altre persone e non usate per costruire prompt o regole, provando anche **C2-CTX v02** in un tempo limitato,
2. verificare che il modello giri **su un telefono Android**, misurando tempi, memoria e batteria,
3. costruire un'**app Android minima** (in React Native, così da poterla portare in seguito anche su iPhone) con proposta, conferma, archivio locale e la possibilità di commentare le proposte,
4. provare **UC-02 e UC-03 in forma ridotta**,
5. fare un **test con alcuni utenti**, raccogliendo i loro commenti.

Il dettaglio di ogni fase (cosa misuro, quando la considero chiusa, cosa mi serve) è in [`PIANO_DI_LAVORO.md`](PIANO_DI_LAVORO.md).

> **Nota sul metodo:** molte prove riportate qui sono diagnostiche e utilizzano note sintetiche già conosciute. I conteggi qualitativi derivano da revisioni preliminari: non vanno presentati come risultati di una validazione indipendente. I test sul solo classificatore non misurano direttamente i popup finali.

## Come è organizzato il repository

```text
├── README.md          # questo file: il percorso complessivo
├── PIANO_DI_LAVORO.md # obiettivo finale, fasi e calendario fino alla consegna
├── esperimenti/       # per ogni esperimento: una descrizione (.md) e i dati (-dati.csv)
└── prototipo/         # nucleo del codice della demo (X0 + C2 + Z + S2-V)
```

Per ogni esperimento c'è un file `.md` che racconta da dove nasce l'idea, cosa ho fatto, cosa si vede e cosa ne concludo, e un file `-dati.csv` con i risultati grezzi su cui si basano le conclusioni (una riga per nota, frammento o azione).

| Esperimento | Punti del percorso | Descrizione | Dati |
|---|---|---|---|
| 01 — Primi test | 1 | [01-primi-test.md](esperimenti/01-primi-test.md) | [CSV](esperimenti/01-primi-test-dati.csv) |
| 02 — Confronto modelli | 3 | [02-confronto-modelli.md](esperimenti/02-confronto-modelli.md) | [CSV](esperimenti/02-confronto-modelli-dati.csv) |
| 03 — Classificazione C0, C1, C2 | 4, 5 | [03-classificazione.md](esperimenti/03-classificazione.md) | [CSV](esperimenti/03-classificazione-dati.csv) |
| 04 — Selettori S0, S1, S2 | 6, 7 | [04-selettori.md](esperimenti/04-selettori.md) | [CSV](esperimenti/04-selettori-dati.csv) |
| 05 — Estrazione X0, X1, X2 | 8, 9 | [05-estrazione.md](esperimenti/05-estrazione.md) | [CSV](esperimenti/05-estrazione-dati.csv) |
| 06 — Contesto P0 e P1 | 10 | [06-contesto-p0-p1.md](esperimenti/06-contesto-p0-p1.md) | [CSV](esperimenti/06-contesto-p0-p1-dati.csv) |
| 07 — Interfaccia I1 e C2-CTX | 11 | [07-interfaccia-i1-c2ctx.md](esperimenti/07-interfaccia-i1-c2ctx.md) | [CSV](esperimenti/07-interfaccia-i1-c2ctx-dati.csv) |
| 08 — Audit I1 e revisione I1-R | 12, 13 | [08-audit-i1-e-revisione-i1r.md](esperimenti/08-audit-i1-e-revisione-i1r.md) | [CSV](esperimenti/08-audit-i1-e-revisione-i1r-dati.csv) |
| 09 — Ripetibilità C2-CTX | 14 | [09-ripetibilita-c2ctx.md](esperimenti/09-ripetibilita-c2ctx.md) | [CSV](esperimenti/09-ripetibilita-c2ctx-dati.csv) |

Script completi, prompt, output originali e manifest con gli hash li conservo in locale. Non li ho caricati qui per non appesantire il repository. I modelli GGUF non sono inclusi.
