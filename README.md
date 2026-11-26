# Assistente AI locale per la gestione delle note

Questo repository raccoglie il prototipo e gli esperimenti che sto svolgendo per la mia tesi. L'obiettivo è costruire un assistente che lavori in locale, interpreti note scritte in linguaggio naturale e **proponga** attività o appuntamenti pertinenti, senza effettuare modifiche automatiche senza conferma.

Il README racconta soprattutto **quali prove ho fatto e perché sono passata da una all'altra**. I dati e gli script completi saranno organizzati nelle cartelle degli esperimenti.

## Da dove sono partita

All'inizio ho preparato note di prova per capire se un piccolo modello linguistico fosse in grado di riconoscere attività, eventi e informazioni che non devono diventare promemoria. Mi sono accorta che non bastava trovare un verbo: il sistema doveva distinguere, per esempio, una cosa da fare da un desiderio, una citazione o un'azione che spetta a un'altra persona.

Ho poi **messo temporaneamente in pausa i confronti** per sviluppare un prototipo utilizzabile sul Mac. Ho collegato estrazione, classificazione, controlli e selezione delle proposte, usando Qwen3-1.7B in locale tramite llama.cpp. Quando la demo ha iniziato a funzionare, sono tornata alla ricerca sui modelli e agli esperimenti più mirati.

## I test svolti, in ordine

### 1. Prime prove sulle note e definizione dei casi

- **Cosa volevo capire:** se il modello riconoscesse task, eventi, date, negazioni e contenuti da ignorare.
- **Cosa ho fatto:** ho costruito note sintetiche e raccolto esempi di errori; in seguito ho usato un development set di 24 note, altri set diagnostici e un insieme sintetico di 40 note.
- **Cosa ho imparato:** dovevo valutare non solo se compariva un popup, ma anche se fosse corretto, completo e attribuito alla persona giusta.

### 2. Sviluppo del prototipo locale

- **Cosa volevo ottenere:** passare dai singoli test a una demo con componenti collegati.
- **Cosa ho fatto:** ho organizzato la pipeline in **X (estrazione) → C (classificazione) → Z (controlli) → S (selezione)** e l'ho fatta lavorare con Qwen3-1.7B sul Mac.
- **Cosa ho imparato:** un errore nel risultato finale può dipendere da componenti diversi; per capirne la causa servono test separati.

### 3. Ricerca e confronto di modelli alternativi

- **Modelli considerati:** Qwen3-1.7B, Qwen3.5-2B e LFM2.5-1.2B.
- **Cosa volevo capire:** se fosse meglio sostituire il modello di riferimento invece di continuare a cambiare prompt e regole.
- **Cosa ho fatto:** ho ripreso la ricerca sulle alternative e confrontato risultati e comportamento sul nostro scenario.
- **Decisione:** ho mantenuto **Qwen3-1.7B** come modello di riferimento per le prove successive. Questo non significa che sia universalmente il modello migliore, ma che è rimasto la scelta di lavoro per il prototipo.

### 4. Classificazione: C0 contro C1

- **Cosa ho cambiato:** il prompt di classificazione, mantenendo 45 frammenti di estrazione condivisi.
- **Risultato sulle 24 note di sviluppo:** classificazioni corrette per entrambi i campi (`kind` e `intent`) da **17/45 a 18/45**.
- **Decisione:** il miglioramento era troppo piccolo e accompagnato da regressioni; ho continuato a lavorare sul classificatore.

### 5. Classificazione: C0 contro C2

- **Cosa ho cambiato:** una nuova versione del prompt C, senza modificare gli altri componenti del confronto.
- **Risultato sugli stessi 45 frammenti:** da **17/45 a 22/45** classificazioni corrette per entrambi i campi, ma con **5 regressioni** su risultati prima corretti.
- **Decisione:** C2 è diventato il classificatore candidato, pur con errori ancora presenti su negazioni, contesti e contenuti citati.

### 6. Selettore delle proposte: S0 contro S1

- **Cosa volevo risolvere:** evitare popup prodotti da frammenti che, isolati, sembravano azioni ma non lo erano.
- **Risultato sulle 24 note di sviluppo:** da **14 a 12 popup**; sono stati eliminati **2 falsi popup noti**, senza perdere proposte valide precedentemente selezionate in quel set.
- **Decisione:** continuare con S1 e provarlo su altre note.

### 7. Selettori S1, S2-V, S2-R e S2-VR

- **Cosa ho fatto:** ho confrontato quattro varianti del selettore su **40 nuove note sintetiche**.
- **Risultato:** S2-V e S2-VR hanno evitato il falso popup su «Magari un giorno imparerò a suonare il violoncello»; le quattro varianti davano lo stesso esito su **39/40 note**.
- **Decisione:** mantenere **S2-V** come selettore candidato, senza confondere il vantaggio su un caso con una validazione generale.

### 8. Estrazione delle informazioni: X0 contro X1

- **Cosa volevo migliorare:** conservare informazioni importanti come date, oggetti e destinatari nelle citazioni estratte.
- **Risultato sulle 40 note note:** X1 recuperava alcuni dettagli, ma peggiorava altri casi e univa azioni separate; valutazione qualitativa **X0: 24 corretti, 7 parziali, 9 errati; X1: 25 corretti, 5 parziali, 10 errati**.
- **Decisione:** non sostituire X0.

### 9. Estrazione atomica: X2 v01 e X2 v02

- **Cosa volevo risolvere:** distinguere più azioni nella stessa nota, mantenendo il relativo contesto.
- **X2 v01:** il modello individuava citazioni utili, ma non produceva intervalli testuali affidabili; gli offset sono stati poi ricostruiti con un allineamento esatto in Python.
- **X2 v02:** su 40 note sono state accettate **39 azioni**. La valutazione finale per nota era **16 corretti, 11 parziali, 13 errati**, peggiore della pipeline X0 sui casi osservati.
- **Decisione:** non adottare X2. Il punto critico era anche l'interfaccia: passare al classificatore solo l'azione breve faceva perdere negazioni e scadenze.

### 10. Proiezione delle citazioni: P0 contro P1

- **Cosa ho confrontato:** **P0**, che passa la sola azione atomica, e **P1**, che passa una clausola più estesa della nota.
- **Risultato su 40 note:** P0 **16 corretti / 12 parziali / 12 errati**; P1 **25 corretti / 4 parziali / 11 errati**. Entrambe generavano 18 popup, ma non sugli stessi casi.
- **Cosa ho imparato:** più contesto rende spesso le proposte più complete, ma può introdurre falsi popup o far perdere attività reali.
- **Decisione:** progettare un'interfaccia che mantenga **azione e contesto separati**, invece di allungare sempre le citazioni.

### 11. Prima interfaccia contestuale: I1 e C2-CTX v01

- **Cosa ho provato:** passare al classificatore l'azione atomica con riferimenti al contesto; ho confrontato **C2 e C2-CTX** sulle stesse **39 azioni**, ottenendo **78 classificazioni valide**.
- **Risultato:** i due classificatori differivano su **16/39 azioni**. C2-CTX recuperava alcuni task, ma confondeva molti eventi con task e attribuiva **SELF a tutte le 39 azioni**, anche quando riguardavano terzi o citazioni.
- **Decisione:** non adottare C2-CTX v01.

### 12. Audit dei dati inviati al classificatore

- **Cosa volevo capire:** se gli errori dipendessero dal modello o da contesti già rappresentati male.
- **Risultato:** nei **50 riferimenti contestuali** trasferiti a I1, la revisione preliminare ha rilevato **29 ruoli incoerenti** e **5 riferimenti troppo ampi**; inoltre non erano state trasferite relazioni tra attività.
- **Decisione:** correggere prima i dati di ingresso e confrontarli con la versione originale.

### 13. Revisione del contesto: I1 contro I1-R

- **Cosa ho cambiato:** i contesti di **18 azioni** appartenenti a 12 note, lasciando invariate le **39 azioni X2** e C2-CTX v01.
- **Risultato:** **35/39 classificazioni identiche** nei sei campi analizzati; solo quattro azioni hanno avuto almeno una differenza. Non è migliorata la distinzione tra eventi e task né l'attribuzione del soggetto.
- **Decisione:** correggere i dati, da solo, non basta. Un cambiamento è comparso perfino a input invariato, quindi serviva un test di ripetibilità.

### 14. Ripetibilità di C2-CTX su input identici

- **Cosa ho fatto:** **20 azioni**, ripetute **3 volte** ciascuna con stessi input e parametri: **60 inferenze**.
- **Risultato:** **60/60 risposte valide**, **19/20 azioni stabili** in tutti i campi; una sola azione oscillava nell'intenzione tra `COMPLETED` e `COMMITTED`.
- **Cosa ho imparato:** il problema principale sembra essere la **correttezza semantica**, più che la variabilità delle risposte. Una risposta ripetuta può comunque essere sbagliata.

## Dove sono arrivata

La configurazione **candidata**, che non ho sostituito con le varianti sperimentali meno affidabili, è:

**`X0 → C2 → Z → S2-V`**

Adesso il passo successivo è progettare **C2-CTX v02**, con uno schema più semplice e regole più esplicite per distinguere eventi, attività, soggetti, citazioni, desideri e negazioni. Prima di considerarlo un miglioramento, sarà necessario testarlo separatamente e poi valutarlo su **note nuove**, non utilizzate per costruire i prompt o le regole.

> **Nota sul metodo:** molte prove riportate qui sono diagnostiche e utilizzano note sintetiche già conosciute. I conteggi qualitativi derivano da revisioni manuali preliminari: non vanno presentati come risultati di una validazione indipendente. I test sul solo classificatore non misurano direttamente i popup finali.

## Come vorrei organizzare i file

```text
tesi-assistente-ai-locale/
├── README.md
├── prototipo/                   # Demo locale (codice pubblicabile)
├── esperimenti/
│   ├── 01-primi-test/
│   ├── 02-confronto-modelli/
│   ├── 03-classificazione-c0-c1-c2/
│   ├── 04-selettori-s0-s1-s2/
│   ├── 05-estrazione-x0-x1-x2/
│   ├── 06-contesto-p0-p1/
│   ├── 07-interfaccia-i1-c2ctx/
│   ├── 08-audit-i1-e-revisione-i1r/
│   └── 09-ripetibilita-c2ctx/
└── documentazione/
```

Per ogni test vorrei caricare, quando disponibili e verificati: **protocollo**, **script**, **input/dataset pubblicabile**, **output originale**, **report di analisi** e **manifest con configurazione e hash**. Prima di pubblicare i materiali controllerò che non contengano dati personali, percorsi locali sensibili, credenziali, file GGUF o archivi inutilmente duplicati.
