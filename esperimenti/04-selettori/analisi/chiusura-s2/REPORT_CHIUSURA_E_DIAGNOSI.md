# Chiusura valutazione UC-01 — 22 novembre 2026

## 1. Policy UC01-S2TEST-029

**Policy adottata per UC-01:** le azioni formulate in modo impersonale («va controllato...») possono essere proposte **quando esprimono un'azione concreta ancora necessaria e pertinente alla nota**. Devono rimanere suggerimenti da confermare, senza creare automaticamente un task né attribuire con certezza l'azione all'utente. Non è sufficiente una descrizione generica o un obbligo esplicitamente di terzi.

**Caso 029:** «Non è necessario comprare la batteria; va invece controllato il caricatore.» Atteso **SI** per *controllare il caricatore*, **NO** per *comprare la batteria*. Tutti i selettori producono nessun popup: omissione **E**.

**Tracciabilità:** il gold precedente riportava `DA_VALUTARE` ed era marcato `PREDEFINITO_DA_CONFERMARE`. Questa decisione avviene **dopo** l'esecuzione del test e non è preregistrata. Il gold originale non viene sovrascritto; per integrità statistica sono riportati sia i risultati con U, sia il ricalcolo post-hoc.

## 2. Risultati (40 note; stessa X0+C2+Z)

| Variante | A | P | E | U | Popup |
|---|---:|---:|---:|---:|---:|
| S1 | 23 | 7 | 10 | 0 | 22 |
| S2-V | 24 | 7 | 9 | 0 | 21 |
| S2-R | 23 | 7 | 10 | 0 | 22 |
| S2-VR | 24 | 7 | 9 | 0 | 21 |

La valutazione **originaria, con policy 029 non decisa**, era: S1 e S2-R 23 A / 7 P / 9 E / 1 U; S2-V e S2-VR 24 A / 7 P / 8 E / 1 U. La policy cambia l'esito assoluto ma **non** la graduatoria. Soltanto la nota 019 distingue le varianti: S2-V e S2-VR eliminano un falso popup. I risultati sono esplorativi, su note sintetiche e con revisione interpretativa, non dimostrazione di significatività o efficacia in produzione.

## 3. Decisione di configurazione

- **Configurazione candidata di ricerca:** `X0+C2+Z+S2-V`.
- **Riferimento immediato:** `X0+C2+Z+S1`, conservato congelato e riproducibile.
- **Baseline storica:** `X0+C0+Z+S0`, conservata separatamente: non è stata rieseguita nel test S2 delle 40 note.
- S2-R non aggiunge un vantaggio misurato; S2-VR ottiene lo stesso risultato di S2-V, ma con maggior complessità.
- **Nessun intervento al codice del prototipo:** la scelta è registrata come candidata sperimentale, non rilascio o sostituzione già avvenuta.

## 4. Diagnosi dei problemi residui

| Caso | Evidenza dalle tracce | Diagnosi e intervento futuro da verificare |
|---|---|---|
| 004 | Frammento intero «Mercoledì telefono all’assicurazione...» = TASK/COMMITTED, Z=PROPOSE; S1 `TEMPORAL_ONLY` | **S**: falso veto temporale su task completo; verificare test unitario per iniziali temporali |
| 005 | Nessun candidato nel CSV | **X0/ingresso**: possibile fallimento estrazione; controllare la traccia grezza prima di attribuire con certezza |
| 011 | «è fissata la prova dell’orchestra» = EVENT/COMMITTED, Z=PROPOSE; S1 `STANDALONE_EVENT_ATTRIBUTE` | **X0+S**: evento frammentato e veto su frammento evento |
| 013 | «La segreteria sta aspettando...» = TASK/COMMITTED, Z=PROPOSE, selezionato | **C2 + gate soggetto**: azione/stato di terzi erroneamente eleggibile |
| 014 | «Il vicino deve sistemare...» = TASK/COMMITTED, Z=PROPOSE, selezionato | **C2 + gate soggetto**: obbligo esplicito di terzi, non task personale |
| 019 | S1 seleziona TASK/TENTATIVE, Z=CLARIFY; S2-V blocca | **S2-V migliora** il veto di aspirazioni vaghe |
| 021, 024 | Aspirazioni vaghe = TASK/TENTATIVE, Z=CLARIFY e S2-V le seleziona | **C2/S**: veto incompleto, evitare adattamento a queste note dello stesso test |
| 028 | «ma domani devo scaricare il QR code» = TASK/COMMITTED, Z=PROPOSE; S1 esclude con `NEGATED_CONTEXT` e `S1_DANGLING_CONNECTOR` | **S**: negazione propagata erroneamente alla clausola positiva |
| 029 | «va invece controllato il caricatore» = FACT/NEGATED, Z=BLOCKED | **C2/Z**: errore semantico prima di S; S non può riabilitare un candidato bloccato |
| 001, 006, 031–033, 036–037 | Popup presenti ma privi di tempo, contesto, referenti, o attività connesse | **X0/ricomposizione + selezione**: conservare data e referenti senza inventare informazioni; analizzare perdita lungo le fasi |
| 030 | 3 azioni nella nota, 1 sola proposta | **Vincolo prodotto**: un popup per nota; non confondere correttezza della proposta con recall completo dei task |

Queste attribuzioni sono **diagnostiche**, non prove causali su ogni singolo componente. Il passo metodologico successivo è congelare questa valutazione, condurre una tassonomia dei fallimenti di X0 su input/output grezzi e definire un esperimento isolato prima di qualunque modifica. Il set 40 non deve essere riutilizzato per ottimizzare nuove regole e poi rivendicare una nuova validazione indipendente.

## 5. Integrità

- Le 40 note sono state esaminate e l'archivio originale conserva 220 righe di candidati.
- Output del confronto originali copiati senza modifiche.
- Gold chiuso e revisione 160 esportati come **derivati post-test**.
- Il confronto della sola variante S2 non dimostra una superiorità generale su modelli, dataset reali o baseline storica.
