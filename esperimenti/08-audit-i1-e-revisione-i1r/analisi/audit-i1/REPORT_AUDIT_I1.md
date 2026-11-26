# UC-01 — Audit dei dati I1 in ingresso a C2-CTX

**Data di analisi:** 25 novembre 2026  
**Fonte primaria:** `c2_ctx_20261125_151925.zip`, file `interfaccia_I1.json` e `flags_contratto.json`.  
**Confronto a monte:** `x0_x1_x2_20261124_233634.zip`, dettagli X2 v02.  
**Stato:** audit tecnico e revisione semantica *preliminare* delle note sintetiche già conosciute; nessuna nuova inferenza, nessun cambiamento del modello, del classificatore o della pipeline di produzione.

## 1. Risultato principale

L'interfaccia I1 è **formalmente valida rispetto ai riferimenti citati**, ma **non semanticamente affidabile**. Nelle 40 note sono presenti 39 azioni X2 validate, 50 riferimenti contestuali e **zero relazioni I1**. Le azioni valide sono in 31 note; 9 note sono senza azioni validate (`014, 016, 018, 022, 023, 029, 036, 037, 040`). Ciò non significa necessariamente che siano prive di attività: è un limite di copertura dell'estrazione X2.

Sono stati verificati tutti i 50 contesti: gli span restituiscono esattamente il testo indicato e ogni `scope` elenca un ID presente nella nota e include l'azione cui è collegato. **Nessun errore di span o scope strutturale rilevato**. La correttezza sintattica non implica però pertinenza della categoria semantica o correttezza della portata.

### Audit qualitativo dei 50 contesti

| Esito della revisione preliminare | Riferimenti |
|---|---:|
| `OK` — ruolo plausibile sul testo | 16 |
| `ROLE_MISMATCH` — categoria non coerente con la prova | 29 |
| `OVERBROAD` — citazione troppo estesa per caratterizzare il ruolo | 5 |
| **Totale** | **50** |

Queste categorie sono **giudizi interpretativi dell'audit**, non metriche automatiche validate da un annotatore indipendente. La classificazione puntuale è nel file `audit_50_riferimenti.csv` e può essere rivista prima di utilizzarla come risultato di tesi.

### Tipologia dei ruoli effettivamente presente

| Ruolo | Riferimenti |
|---|---:|
| `time` | 24 |
| `recipient` | 18 |
| `place` | 5 |
| `condition` | 3 |

**Assenti dall'intero payload I1:** `polarity`, `modality`, `completion`, `speaker`, `discourse`, `antecedent`. La loro assenza **non dimostra** che nessun elemento della nota li esprima, ma indica che l'adattatore non li codifica in modo esplicito. Il classificatore deve quindi interpretarli dal testo della nota, se vi riesce.

## 2. Errori riproducibili e casi guida

| Nota | Dato I1 rilevato | Diagnosi |
|---|---|---|
| `001` | «entro lunedì mattina» sotto `condition` | Scadenza temporale; ruolo `time` più appropriato, eventualmente con sottotipo `deadline` |
| `006` | «caricare» sotto `time` | Ruolo manifestamente errato: è il verbo dell'azione |
| `008` | «La visita con l’oculista è confermata» sotto `time`; «per venerdì alle 15:30» come seconda *azione* | L'estrazione X2 spezza un evento in parte predicativa e parte temporale; problema **a monte** dell'adattatore |
| `010` | «il 12 dicembre alle 8» sotto `place` e `recipient` | Citazione temporale etichettata con ruoli sbagliati |
| `017` | Azione «invii», nessun contesto | Non viene registrato che il soggetto è **il fornitore** e la frase è una disposizione contrattuale |
| `019` | «imparerò a suonare il violoncello» sotto `recipient` | Ruolo errato e perdita del qualificatore «Magari un giorno» |
| `020` | «Mi piacerebbe» sotto `time` | Qualificatore di desiderio, non un tempo |
| `021` | «Forse cambierò città» sotto `time`; seconda azione «non ho deciso nulla» | La frase di incertezza viene trattata come azione autonoma invece di qualificare la precedente |
| `025` | «ci pensa già Alessia» sotto `recipient` | Non codifica soggetto terzo, completamento/delega e negazione dell'obbligo dell'utente |
| `026` | Relazione X2 `after` presente nella traccia accettata ma assente in I1 | Perdita documentata della relazione; qualità semantica di `after` da controllare prima di riutilizzarla |
| `028` | Solo «devo scaricare il QR code» sopravvive; «domani» trasferito correttamente | L'azione negata «Non devo stampare i biglietti» è già scartata in X2; non può essere ripristinata dall'adattatore |
| `030`, `033` | `place`/`recipient` assegnati a porzioni estese della nota che contengono altre attività | Ruoli errati e rischio di contaminazione fra azioni |
| `034` | «l’incontro con il gruppo di lettura» sotto `place` e `recipient` | Non è un luogo; il luogo reale «Alla biblioteca comunale» non è rappresentato |
| `038`, `039` | Citazioni riportate con contesti come `time` e `recipient` | Non viene codificato in modo affidabile il fatto che le azioni appartengono a citazioni/testi di prova |

**Nota:** nei casi 008 e 021, anche una mappatura perfetta dei ruoli non basterebbe: X2 ha individuato unità atomiche inappropriate. I problemi di estrazione e quelli di proiezione sono distinti.

## 3. Perdita nell'adattatore X2 → I1

Il file originale `flags_contratto.json` contiene **17 segnalazioni**: 16 `ROLE_UNSUPPORTED` per il ruolo X2 `object_reference` e 1 `RELATIONS_NOT_PROJECTED` nel caso 026. Si tratta di perdite **registrate**, non di una ricostruzione ipotetica.

La variante X2 v02 aveva prodotto 55 azioni grezze e validato 39 azioni. I1 riutilizza queste 39 azioni: non può recuperare i 16 elementi grezzi che non hanno superato la validazione. Una relazione era presente in X2 validato, nessuna è presente in I1. Non occorre supporre che la relazione fosse semanticamente corretta: occorre soltanto registrare che il trasferimento l'ha omessa.

## 4. Interpretazione rispetto agli errori di C2-CTX

Le categorie errate in I1 possono **contribuire** agli errori del classificatore; non è però possibile attribuire loro causalmente tutti gli errori di C2-CTX senza un intervento isolato sull'input. Il classificatore riceve anche la nota originale, quindi avrebbe talvolta gli indizi per riconoscere desiderio, soggetto e citazione anche quando il riferimento strutturato è errato. L'assegnazione di `SELF` a tutte le 39 azioni e la trasformazione di eventi in task devono essere valutate come problemi **potenzialmente sia di input sia di classificazione**, non imputati automaticamente soltanto a I1.

Non è stato eseguito Z né S2-V in questo audit; non vengono formulate affermazioni su nuovi popup.

## 5. Decisione e percorso controllato

**Non implementare ancora C2-CTX v02.** Prima:

1. Congelare l'audit attuale, senza alterare i file X2 o I1 originali.
2. Preparare una rappresentazione **I1-R (revisionata)**, separata e versionata, su un piccolo set di casi di diagnosi, con annotazioni esplicite per `modality`, `polarity`, `speaker/subject_owner`, `completion` e `discourse`. Distinguere `action_quote` e qualificatori; non inventare citazioni e non convertire una frase non azionale in task.
3. Definire criteri *fail-closed* quando un ruolo o uno scope sono ambigui: marcare `unresolved`, non sostituire con un'etichetta indovinata. Le azioni non estratte da X2 rimangono **mancanti**.
4. Confrontare **a classificatore C2-CTX v01 identico** gli input I1-originale e I1-R per isolare l'effetto della qualità dell'input; includere confronti `kind/intent` e attributi contestuali. Qualsiasi revisione manuale costituisce un *intervento diagnostico con input assistito*, non una misura automatica di estrazione.
5. Solo dopo, se serve, progettare C2-CTX v02 su dati congelati e validarla su note indipendenti. Non riutilizzare le 40 note come holdout.

La configurazione candidata del prototipo rimane **X0+C2+Z+S2-V**.

## 6. File

- `audit_50_riferimenti.csv`: ogni riferimento con citazione, ruolo, span/scope e valutazione preliminare.
- `sintesi_40_note.csv`: copertura delle azioni e distribuzione dei problemi per nota.
- `flags_adattatore_originali.json`: segnalazioni originali di conversione.
- `metriche.json`: conteggi verificabili e limiti dichiarati.
