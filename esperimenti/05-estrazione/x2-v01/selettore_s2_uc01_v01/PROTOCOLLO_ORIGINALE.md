# UC-01 — Protocollo preregistrato per il prossimo esperimento sul selettore S

Data: 21 novembre 2026 — fase di progettazione, **nessuna inferenza S2 ancora eseguita**.

## 1. Stato e motivazione

- Development: 24 note; S0 vs S1 con X0+C2+Z costanti: 14 vs 12 popup, due falsi popup eliminati (MAIN-076 e MAIN-113) e nessuna selezione valida persa nel set esaminato.
- Holdout sintetico successivo: 32 note, 53 frammenti; baseline X0+C0+Z+S0 vs candidata X0+C2+Z+S1: 13 popup ciascuna, 6 selezioni differenti. La candidata non ha dimostrato superiorità conclusiva.
- Regressioni diagnosticate: HOLD-004 (descrizione del commercialista scelta al posto dell'invio della scansione), HOLD-021 (aspirazione vaga proposta). Miglioramenti HOLD-006, HOLD-019, HOLD-023; HOLD-028 differenza neutra. Limiti comuni HOLD-007/009 (evento confermato non proposto), HOLD-016 (azione non estratta), HOLD-001/006/008 (informazioni temporali separate).
- Il holdout32 è stato ispezionato per decidere i prossimi interventi: **non può essere riutilizzato come prova indipendente di S2**.

## 2. Domanda sperimentale

A parità di frammenti X0, classificazioni C2, decisioni Z e parametri runtime, un selettore S2 con verifica aggiuntiva di autonomia e priorità della proposta migliora la pertinenza dei popup rispetto a S1 senza perdere attività valide?

## 3. Variabile controllata

- Ramo A: X0 + C2 + Z + S1 (riferimento attuale).
- Ramo B: X0 + C2 + Z + S2 (sperimentale).
- X0 eseguita una volta per nota, C2 una volta per frammento, Z applicato una sola volta; i due selettori ricevono le stesse istanze immutabili.
- S2 non può modificare `kind`, `intent`, `evidence`, date, Z, né recuperare frammenti mancanti. Non può rendere eleggibile un candidato bloccato da Z. Si conserva il massimo di un popup per nota.
- Congelare SHA-256 di tutti i file prima del test e documentare differenze del solo selettore.

## 4. Ipotesi e possibili componenti di S2

H1 — Una proposta informativa o ipotetica non deve prevalere su un'attività concreta: introdurre una verifica prudente di **azione effettivamente espressa nel frammento**, evitando una lista rigida di sole parole chiave e senza usare identificativi o frasi del dataset.

H2 — La distinzione fra un'aspirazione generica e un'azione da intraprendere deve usare il contesto linguistico della proposizione, non la sola etichetta C2. Un semplice futuro o un oggetto nominale non basta di per sé a rendere il candidato autonomo.

H3 — Fra candidati tutti eleggibili, dare una precedenza motivata a impegni espliciti rispetto a constatazioni incidentalmente classificate TASK. Il cambio di ranking va misurato separatamente dai nuovi veto.

H4 — Un EVENT confermato e autonomo non deve essere bloccato da nuove regole. Se i casi HOLD-007 e HOLD-009 sono esclusi già da S1, analizzare la ragione specifica senza costruire un'eccezione sui due esempi.

Per isolamento causale, considerare due sottovarianti: S2-V (solo veto) e S2-R (solo ranking), poi S2-VR solo se entrambe sono promettenti. Documentare l'effetto incrementale di ciascuna.

## 5. Casi di regressione obbligatori (diagnostici, non dati di validazione)

- MAIN-060: recuperare mail al fornitore; MAIN-024: mantenere almeno un task valido; MAIN-097 e MAIN-118: preservare task espliciti.
- MAIN-076 e MAIN-113: non ripristinare falsi popup.
- HOLD-004: preferire l'azione della scansione se X0 e Z la preservano; HOLD-021: rifiutare l'aspirazione vaga; HOLD-006: non perdere evento valido; HOLD-019/023: non reintrodurre falsi popup.
- HOLD-007/009, 016 e casi con date separate: riportare come limiti di altri componenti, se S2 non può risolverli senza cambiare l'architettura.

## 6. Dataset e protocollo

1. Usare le 24 note development e le 32 holdout **solo come set diagnostici noti**. Le performance su tali insiemi non sono indipendenti.
2. Predisporre un **nuovo test set** non usato per scrivere S2, idealmente con annotazioni umane cieche alle predizioni e criteri fissati prima dei risultati. Includere task espliciti, eventi, negazioni, citazioni, aspirazioni, frasi informative, frasi senza verbo d'azione, più task, date disgiunte, anafore e falsi positivi lessicali.
3. Non leggere il gold durante l'inferenza. Conservare ogni candidato e diagnosi S1/S2, non solo il popup vincente.
4. Valutare la bontà del risultato con categorie A (corretto e autosufficiente), P (valido ma incompleto), E (errato, mancante o improprio), U (non decidibile prima di una policy), più causa principale X0/C2/Z/S.
5. Separare casi con popup inappropriato (falso positivo), mancata proposta dovuta a S (falso negativo), proposta semanticamente incompleta, sostituzione valida e assenza corretta di popup.

## 7. Metriche predefinite

- Precisione dei popup su casi giudicabili = popup appropriati / popup mostrati (specificare se P è contato a parte).
- Recall per nota delle opportunità proponibili = note con proposta valida / note con almeno un'opportunità valida, includendo i casi senza popup.
- Numero di regressioni su task/eventi espliciti; nuovi falsi popup; casi risolti; sostituzioni neutre.
- Risultati A/P/E/U per ramo; matrice appaiata dei cambi; latenza aggiuntiva del solo selettore.
- Intervalli di incertezza ove sensato; non interpretare piccole differenze su campioni ridotti come prova statistica.

## 8. Criteri di promozione (prima di vedere il nuovo test)

- Nessuna regressione grave su attività concrete già correttamente proposte da S1 nei casi diagnostici obbligatori.
- Riduzione di falsi popup sui nuovi dati, senza riduzione sostanziale del recall di note con azioni/eventi validi.
- Vantaggio qualitativo documentato sul test nuovo, con analisi e motivazioni dei casi discordanti.
- In assenza di evidenza consistente, conservare S1 come candidata e mantenere la baseline originale separata.

## 9. Integrità e limiti

Qualunque modifica di regola dopo lettura del nuovo test obbliga a considerarlo un nuovo development set e a predisporre un altro test indipendente. Il dataset sintetico non sostituisce la verifica futura su note reali e privacy-preserving. Questo protocollo non attribuisce miglioramenti a C2 o X0, poiché tali componenti saranno identici nei due rami.
