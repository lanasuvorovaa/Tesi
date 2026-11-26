# UC-01 — Revisione diagnostica C2 vs C2-CTX

**Data analisi:** 25 novembre 2026. **Fonte:** `c2_ctx_20261125_151925.zip`. La valutazione semantica qui riportata è una prima revisione assistita da confermare da parte del ricercatore. Il set di 40 note è già stato usato in precedenti iterazioni; non è un holdout indipendente.

## Integrità del confronto

- Dataset dichiarato: **40 note**; **31 note** contengono almeno una delle azioni X2 validate oggetto del confronto.
- **39 azioni** appaiate; **78 classificazioni** prodotte e valide rispetto agli schemi (39 C2, 39 C2-CTX).
- Nessun gold letto dal runner. Z e S2-V **non** sono stati eseguiti; non ci sono metriche reali sui popup.
- Configurazioni e hash riportati nel `manifest.json` allegato al run. Modello e azioni X2 condivisi; cambia l'interfaccia/prompt di classificazione.

## Risultati osservati

- C2: 24 TASK, 9 FACT, 6 EVENT; C2-CTX: **38 TASK, 1 EVENT**.
- Differenze di `kind` o `intent`: **16/39** azioni; 23 restano invariate per tali campi.
- Nella revisione dei 16 cambi: **4 plausibili miglioramenti**, **10 peggioramenti**, **2 non determinabili univocamente**. Sono giudizi circoscritti ai cambi, non accuratezza aggregata del classificatore.
- C2-CTX attribuisce `subject_owner=SELF` **39/39** volte; `polarity=POSITIVE` **37/39**, `completion=DONE` **11/39**. La sola validità dello schema JSON non assicura correttezza semantica.

## Esempi verificati

**Progressi:** caso 002 `rinnovare la tessera` FACT/INFORMATIONAL → TASK/COMMITTED; caso 030 azione `stampare l’etichetta` FACT/INFORMATIONAL → TASK/COMMITTED; caso 032 `controllo il numero di serie` FACT/INFORMATIONAL → TASK/COMMITTED; caso 024 intenzione di maratona COMMITTED → TENTATIVE.

**Regressioni critiche:** casi 008, 009, 011 e 034: eventi fissati o confermati diventano `TASK/COMMITTED`. Caso 025: `ci pensa già Alessia` passa da `TASK/NEGATED` a `TASK/COMMITTED`, con erroneo `SELF`. Caso 020: desiderio di aprire un laboratorio diventa `TASK/COMMITTED`. Casi 038 e 039: contenuti citati diventano task impegnativi.

**Attributi incoerenti anche con kind/intent invariati:** caso 028 (`devo scaricare il QR code` dopo una negazione riferita a un'altra azione) risulta `completion=DONE` nonostante sia un'azione futura; caso 026 azione `non devo andare in ambulatorio` viene resa `POSITIVE` e `DONE`. Nel caso 013, `sta aspettando una risposta dal corriere` appartiene alla segreteria, non all'utente, eppure `subject_owner=SELF`. 

**Qualità dell'input:** alcuni elementi estratti sono semanticamente non autonomi, come `prenotata` (012) o `per venerdì alle 15:30` (008 a2); alcuni `context_refs` hanno ruoli discutibili (es. etichetta `time` sulla frase intera della visita in 008). Questi sono limiti a monte della classificazione, da non attribuire automaticamente a C2-CTX.

## Decisione

**Non promuovere C2-CTX v01** né collegarlo direttamente a Z/S2-V. Non è un miglioramento affidabile: i recuperi su task espliciti sono controbilanciati da errori importanti su eventi, soggetto, negazione e testo citato. **Conservare X0+C2+Z+S2-V come configurazione candidata**.

## Prossimo esperimento consigliato

1. **Diagnostica del contratto**: annotare per ogni azione `kind`, `intent`, soggetto, negazione, stato e la natura di evento/citazione; convalidare la portata dei contesti I1 e distinguere errori X2/I1 da errori C2-CTX.
2. **Separare decisioni e metadati**: introdurre istruzioni e vincoli espliciti per EVENT, per `OTHER`/`QUOTED` e per negazione; evitare valori `SELF` e `DONE` predefiniti. Questo costituirebbe **una nuova versione del classificatore** da congelare e testare, non una semplice correzione di formattazione.
3. Ripetere prima la diagnosi sulle 39 azioni, con C2 e altri componenti congelati; se promettente, utilizzare un nuovo testset indipendente e soltanto dopo provare l'effetto end-to-end sui popup.

## Limitazioni

Il dataset è piccolo, sintetico e già conosciuto; alcune annotazioni rimangono contestuali e vanno sottoposte a revisione umana. La tabella `revisione_39_azioni.csv` contiene il confronto completo e l'annotazione dei soli cambi di etichetta. Non usare questi numeri come metriche di accuratezza sull'intero sistema.
