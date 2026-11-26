# UC-01 — Valutazione diagnostica dell'interfaccia X2: P0 contro P1

**Fonte:** `proiezioni_20261124_235803.zip`. **Data dell'esperimento:** 24 novembre 2026. **Confronto:** stesse estrazioni X2 congelate, stessa C2, Z e S2-V; cambia soltanto la proiezione dell'evidenza passata alla pipeline.

## Integrità e limiti

- 40 note, 80 valutazioni, nessun errore di pipeline rilevato nel CSV; entrambe le varianti hanno 39 citazioni validate e 18 popup.
- `gold_loaded=false` nell'esperimento: il gold non viene fornito alla pipeline. La valutazione successiva usa il gold con policy chiusa dopo il test S1/S2. La nota 029 ha una decisione di policy **post-test**, non preregistrata.
- Le 40 note erano note prima di progettare P1: questi dati costituiscono **diagnostica di sviluppo**, non validazione indipendente. La classificazione A/P/E contenuta nei file è una **revisione assistita preliminare**, da confermare manualmente.
- La decisione `CLARIFY` è stata conteggiata come popup quando riportata come `SI`: su desideri vaghi può costituire un falso popup rispetto alla policy del set.
- Lo `Z_actual=BLOCKED` nelle tracce riflette la mancanza di capacità applicative verificate nel sandbox e non contraddice il popup proposto in modalità diagnostica; non sono state effettuate scritture.

## Risultati qualitativi

| Esito | P0 atomica | P1 clausola |
|---|---:|---:|
| A — corretto e autonomo, oppure corretta non-proposta | 16 | 25 |
| P — pertinente ma incompleto, non atomico o senza vincoli essenziali | 12 | 4 |
| E — falso popup o attività attesa omessa | 12 | 11 |
| **Totale** | **40** | **40** |

Il confronto è appaiato. La trasformazione migliora soprattutto la completezza dei popup, non il numero di proposte: **18 popup in entrambe le varianti**. Le differenze qualitative sono concentrate in 13 note; in 27 le categorie A/P/E non cambiano.

### Progressi osservati

- **001, 003, 005, 006, 007, 009, 034, 035:** P1 recupera scadenze, oggetti, destinatari e contesto prima mancanti, rendendo più autonome le proposte.
- **002:** P0 omette un task esplicito; P1 lo propone.
- **017:** P0 propone erroneamente `invii` come task dell'utente; P1 riconosce il contesto contrattuale e non produce popup.
- **032:** P1 recupera un popup pertinente, ma ingloba due attività in una sola citazione; rimane un esito parziale.

### Regressioni e limiti irrisolti

- **004 — regressione:** P0 propone la telefonata, seppur incompleta; P1 non propone nulla a causa del veto `TEMPORAL_ONLY` applicato alla citazione lunga, nonostante `TASK/COMMITTED`.
- **021 — regressione:** P0 non propone nulla; P1 propone `Forse cambierò città` perché separa questa clausola dalla conclusione `non ho deciso nulla`.
- **019, 024:** P1 include indizi di aspirazione (`Magari un giorno`, `Sarebbe bello`) e C2 indica `TENTATIVE`, ma la pipeline continua a emettere un popup di chiarimento: l'ampliamento del contesto non garantisce il veto desiderato.
- **013:** entrambe le varianti propongono un'azione di terzi (`La segreteria sta aspettando...`).
- **028:** entrambe perdono l'azione positiva di scaricare il QR code per `NEGATED_CONTEXT`, pur riconoscendo `TASK/COMMITTED`.
- **029:** entrambe omettono `controllare il caricatore`, considerato proponibile secondo policy **post-test**.
- **031, 032:** P1 ingloba due attività nello stesso popup; migliore completezza non equivale ad atomicità.
- **036, 037:** nessuna delle due proiezioni recupera le azioni non estratte a monte.
- **011, 012:** eventi confermati ancora omessi.

## Interpretazione e decisione

P1 fornisce un **miglioramento diagnostico** della completezza semantica (25 A contro 16 A), ma introduce due regressioni importanti e lascia aperti errori di selezione, negazione e separazione di compiti. La proiezione di una clausola più ampia non costituisce, da sola, un'interfaccia robusta fra X2 e C2.

**Decisione:** non promuovere P1 nella configurazione candidata. Mantenere **X0 + C2 + Z + S2-V** come riferimento sperimentale stabile. Conservare P1 come variante promettente da perfezionare e testare su nuovi dati, evitando di ottimizzarla per queste 40 note già viste.

**Passo successivo raccomandato:** progettare un'interfaccia che conservi separatamente (1) la citazione atomica per il candidato, (2) la clausola e i modificatori come contesto interpretativo e (3) i riferimenti testuali verificati; introdurre controlli di coerenza a livello di nota per intenzioni non decise e negazioni locali; valutare esplicitamente l'atomicità del popup e prevenire veti errati come `TEMPORAL_ONLY`. Questo implicherebbe una **nuova versione sperimentale dell'interfaccia** e, se necessario, una nuova modalità di input di C2: non andrebbe descritta come C2 invariata se il classificatore riceve informazioni aggiuntive fuori dal normale campo `evidence`.

## Allegati

- `revisione_80_P0_P1.csv`: motivazione A/P/E per ogni coppia nota-variante;
- `sintesi_40_note.csv`: differenze affiancate per nota;
- `confronto_note_originale.csv`, `confronto_candidati_originale.csv`, `audit_proiezioni_originale.csv`, `manifest_originale.json`, `report_runner_originale.md`: file di partenza conservati senza modifiche.
