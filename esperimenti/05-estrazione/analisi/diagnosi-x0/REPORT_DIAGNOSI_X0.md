# Diagnosi strutturale UC-01: X0 e completezza semantica

**Data:** 22 novembre 2026  ·  **Stato:** analisi retrospettiva di tracce congelate, nessun nuovo test o modifica al codice.

## Scopo e base probatoria

Esaminate tutte le 40 note del test S2, le relative 40 tracce JSON originali (estrazione grezza, citazioni validate, classificazione C2, gate Z, decisione S e popup) e la revisione post-test. L’allegato CSV contiene una riga per ogni nota. I casi sotto sono selezionati perché più informativi per la prossima fase. Le attribuzioni sono diagnosi motivate, non risultati di esperimenti causali di ablation.

**Cautela cruciale su Z:** le tracce distinguono `sandbox_gate` da `actual_gate`. Nella simulazione i candidati possono avere `sandbox_gate=PROPOSE`, mentre `actual_gate=BLOCKED` per capacità non verificate e controllo globale duplicati indisponibile. Questa diagnosi riguarda esclusivamente la *proposta simulata*, non la capacità di creare davvero task o eventi.

## Evidenze principali

1. **Estrazione citazioni non letterali:** 005 e 031 mostrano che la risposta grezza X0 include citazioni respinte dal validatore (`QUOTE_0_INVALID_OR_NOT_UNIQUE`). Non è corretto sostenere che X0 non abbia generato alcuna proposta di estrazione: la generazione esiste, ma fallisce la verifica letterale. 016, 022 e 023 presentano problemi simili senza necessariamente costituire errori di popup rispetto al gold.

2. **Frammentazione con perdita del contesto:** 001 e 006 separano scadenze o luogo dall’azione; 011 perde «Sabato pomeriggio»; 036 e 037 mantengono pronomi anaforici che richiedono la nota originale. La ricomposizione andrebbe verificata come fase distinta dalla classificazione.

3. **Veti del selettore falsi:** 004 è un task completo marcato `TEMPORAL_ONLY`; 028 contiene una seconda clausola positiva `TASK/COMMITTED`, ma viene esclusa tramite `NEGATED_CONTEXT`. Non sono primariamente errori X0.

4. **Classificazione e soggetto dell’azione:** 013, 014 e 017 producono proposte riconducibili a soggetti terzi; 021 e 024 trasformano aspirazioni vaghe in opportunità di popup. 029 è un’azione concretamente necessaria che C2 marca `FACT/NEGATED` e Z blocca.

5. **Un solo popup per nota:** 030 estrae più task, ma ne seleziona uno solo secondo il vincolo del prodotto. Questo non è di per sé un errore S2-V; va misurato separatamente come copertura delle attività.

## Tracciamento dei casi prioritari

| Caso | Frammenti validati X0 | C2 / Z essenziali | S2-V: popup | Diagnosi |
|---|---|---|---|---|
| 001 | Devo spedire il campione al laboratorio // entro lunedì mattina | C1: Devo spedire il campione al laboratorio [TASK/COMMITTED; Z=PROPOSE] // C2: entro lunedì mattina [TASK/COMMITTE… | Devo spedire il campione al laboratorio | Scadenza separata dalla frase azione |
| 004 | Mercoledì telefono all’assicurazione per chiedere la nuova polizza | C1: Mercoledì telefono all’assicurazione per chiedere la nuova polizza [TASK/COMMITTED; Z=PROPOSE] | Nessuno | Frase completa erroneamente marcata TEMPORAL_ONLY |
| 005 |  |  | Nessuno | X0 ha prodotto una citazione non letterale, poi respinta |
| 006 | Devo caricare il documento firmato // sul portale entro le 18 | C1: Devo caricare il documento firmato [TASK/COMMITTED; Z=PROPOSE] // C2: sul portale entro le 18 [TASK/COMMITTED;… | Devo caricare il documento firmato | Complemento luogo/scadenza separato dal task |
| 011 | è fissata la prova dell’orchestra | C1: è fissata la prova dell’orchestra [EVENT/COMMITTED; Z=PROPOSE] | Nessuno | Il frammento perde la data e viene escluso |
| 013 | La segreteria sta aspettando una risposta dal corriere | C1: La segreteria sta aspettando una risposta dal corriere [TASK/COMMITTED; Z=PROPOSE] | La segreteria sta aspettando una risposta dal corriere | Stato di soggetto terzo proposto come task |
| 014 | Il vicino deve sistemare il cancello del cortile | C1: Il vicino deve sistemare il cancello del cortile [TASK/COMMITTED; Z=PROPOSE] | Il vicino deve sistemare il cancello del cortile | Obbligo del vicino presentato come attività dell’utente |
| 017 | Il contratto prevede // che il fornitore invii // un rapporto mensile | C1: Il contratto prevede [FACT/INFORMATIONAL; Z=BLOCKED] // C2: che il fornitore invii [TASK/COMMITTED; Z=PROPOSE]… | Nessuno | Subordinata contrattuale frammentata e proposta come task personale |
| 021 | Forse cambierò città // ma per ora non ho deciso nulla | C1: Forse cambierò città [TASK/TENTATIVE; Z=CLARIFY] // C2: ma per ora non ho deciso nulla [FACT/TENTATIVE; Z=BLOC… | Forse cambierò città | Possibilità generica trattata come task proponibile |
| 024 | Sarebbe bello partecipare a una maratona un giorno | C1: Sarebbe bello partecipare a una maratona un giorno [TASK/TENTATIVE; Z=CLARIFY] | Sarebbe bello partecipare a una maratona un giorno | Desiderio generico proposto |
| 028 | Non devo stampare i biglietti // ma domani devo scaricare il QR code | C1: Non devo stampare i biglietti [TASK/NEGATED; Z=BLOCKED] // C2: ma domani devo scaricare il QR code [TASK/COMMI… | Nessuno | Task positivo bloccato per negazione della clausola precedente |
| 029 | Non è necessario comprare la batteria // va invece controllato il caricatore | C1: Non è necessario comprare la batteria [TASK/NEGATED; Z=BLOCKED] // C2: va invece controllato il caricatore [FA… | Nessuno | Azione impersonale positiva classificata FACT/NEGATED |
| 030 | Per il viaggio devo pesare la valigia // stampare l’etichetta // prenotare il taxi | C1: Per il viaggio devo pesare la valigia [TASK/COMMITTED; Z=PROPOSE] // C2: stampare l’etichetta [FACT/INFORMATIO… | Per il viaggio devo pesare la valigia | Più task estratti; uno solo selezionato |
| 031 | inviare la ricevuta alla contabilità | C1: inviare la ricevuta alla contabilità [TASK/COMMITTED; Z=PROPOSE] | inviare la ricevuta alla contabilità | Prima azione scartata; resta la seconda senza riferimento domani |
| 032 | Prima controllo il numero di serie // poi apro la segnalazione al supporto | C1: Prima controllo il numero di serie [FACT/TENTATIVE; Z=BLOCKED] // C2: poi apro la segnalazione al supporto [TA… | poi apro la segnalazione al supporto | Seconda azione senza antecedente esplicito; prima classificata FACT |
| 033 | Per il mercatino sabato preparo i cartellini // porto il resto // avviso Martina | C1: Per il mercatino sabato preparo i cartellini [TASK/COMMITTED; Z=PROPOSE] // C2: porto il resto [TASK/COMMITTED… | porto il resto | Selezione «porto il resto» senza contesto mercatino |
| 036 | Il modulo per l’iscrizione l’ho scaricato // Quello firmato devo consegnarlo venerdì | C1: Il modulo per l’iscrizione l’ho scaricato [FACT/INFORMATIONAL; Z=BLOCKED] // C2: Quello firmato devo consegnar… | Quello firmato devo consegnarlo venerdì | «Quello firmato» necessita della frase precedente |
| 037 | L’indirizzo del deposito // ci passo lunedì per ritirare le casse | C1: L’indirizzo del deposito [FACT/INFORMATIONAL; Z=BLOCKED] // C2: ci passo lunedì per ritirare le casse [TASK/CO… | ci passo lunedì per ritirare le casse | «ci passo» dipende dal deposito menzionato prima |

## Ipotesi per un futuro esperimento isolato (non implementate)

**H-X0-L (letteralità):** misurare percentuale di citazioni raw accettate, distinguendo output non esatti, duplicati e limiti di estrazione. Non rilassare il validatore senza sperimentazione di sicurezza.

**H-X0-C (completezza):** confrontare l’estrazione corrente con una variante che preservi azione e vincoli in una stessa citazione, mantenendo C2, Z e S2-V congelati. Misurare autonomia della proposta, scadenze/luoghi conservati e nuovi errori.

**H-R (ricomposizione):** confrontare la proposta del frammento con una versione di presentazione che recuperi *solo* span originali verificati della stessa nota, senza cambiare X0 o la classificazione. Trattarla come intervento distinto da H-X0-C.

**H-S (veto):** i casi 004 e 028 richiedono analisi del selettore, ma non devono essere corretti insieme a X0 nel medesimo test.

**H-C (soggetto / obblighi):** 013/014/017/021/024/029 richiedono un test distinto sul classificatore o su un gate di pertinenza, non sulla ricomposizione.

## Priorità e decisioni

- **Non modificare ancora X0, C2, Z o S2-V.** Congelare questo report come diagnosi del test S2 delle 40 note.
- **Primo esperimento consigliato:** confronto isolato della preservazione dei vincoli testuali in X0, con C2+Z+S2-V fissi; in alternativa, ricomposizione a valle come esperimento autonomo.
- **Metriche:** quote raw validate; task/eventi coperti; scadenze, luoghi e referenti presenti nel popup; accuratezza A/P/E; falsi popup; tempo e numero di chiamate del modello.
- **Valutazione:** casi già noti solo per sviluppo/debugging; qualunque nuova pretesa di generalizzazione richiede nuove note o annotazione esterna indipendente.

## Riproducibilità

- Sorgente delle tracce: `nuove_note_20261122_192516.zip` (file `dettagli/UC01-S2TEST-*.json`).
- Riferimento delle valutazioni: `Chiusura_UC01_S2_2026-11-22.zip`, file `revisione_160_POLICY_CHIUSA.csv` (decisione sul caso 029 post-test).
- `tracciamento_40_note.csv` conserva note originali, estrazione raw, quote validate, C2/Z, ragioni S, popup ed etichette della revisione.
- Non sono state rieseguite inferenze e non sono state alterate le configurazioni congelate.
