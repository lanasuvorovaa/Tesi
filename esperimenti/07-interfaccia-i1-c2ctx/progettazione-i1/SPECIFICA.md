# UC-01 — Interfaccia contestuale strutturata I1 (specifica v0.1)

**Stato:** progettazione, non implementazione end-to-end né nuovo risultato sperimentale. **Base empirica:** test P0/P1 (40 note sintetiche già conosciute): P0 16 A/12 P/12 E, P1 25 A/4 P/11 E; ambedue 18 popup; revisione assistita preliminare. Il vantaggio di P1 riguarda la completezza, ma rimangono regressioni (004, 021) e falsi popup (019, 024).

## 1. Problema e obiettivo

P0 consegna a C2 citazioni atomiche troppo scarne; P1 passa citazioni lunghe, migliorando il contesto ma talvolta includendo più attività. I1 deve **separare l'unità operativa dalla prova testuale e dai qualificatori semantici**. Nessuna stringa ricostruita viene dichiarata citazione della nota. Il sistema continua a proporre al massimo un popup per nota; non crea direttamente eventi o task.

## 2. Contratto tra estrazione e classificazione

Un record `note` contiene `note_id`, `text`, `reference_datetime`, `actions[]` e `relations[]`. Ogni `action` possiede:

- `id`: identificatore locale univoco;
- `action_evidence`: un frammento **contiguo** della nota, con `quote` e `span` calcolato/controllato in Python; deve individuare una sola azione quando possibile;
- `context_refs[]`: prove letterali associate, ognuna con `quote`, `span`, `role`, `scope`, `source` (solo `explicit_text` nel primo prototipo), `confidence_policy` (`verified`, non probabilità del modello);
- `interpretation`: **non ancora classificata**, per evitare che l'estrattore decida già intenzione, tempo o proponibilità;
- `provenance`: modalità di estrazione e versione del parser, per replay.

I `role` ammessi includono `time`, `place`, `recipient`, `object`, `polarity`, `modality`, `condition`, `completion`, `speaker`, `discourse`, `antecedent`. Il campo `scope` è **un ID azione, un insieme esplicito di ID o `note_global`**; mai assegnare automaticamente un `non` a tutte le azioni della nota. `relations[]` usa `source_action_id`, `target_action_id`, `type` (`before`, `after`, `depends_on`, `contrasts_with`, `same_event`), `evidence` e `span` verificati. La relazione non autorizza deduzioni implicite.

**Indici:** `[start, end)` misurati sui caratteri Python; ogni `text[start:end]` deve coincidere *esattamente* con la citazione. Non chiedere offset al modello; allineamento deterministico con rifiuto di occorrenze ambigue.

## 3. Confine del classificatore: nuova modalità esplicita

Non chiamare questa modalità semplicemente `C2` invariata. Il classificatore attuale C2 accetta una `evidence` lineare; se riceve azione più contesto separati, cambia la **semantica del suo input**. Denominiamo `C2-CTX` (versione sperimentale dell'interfaccia/prompt, da congelare e confrontare). L'input deve includere:

1. `action_evidence.quote` (azione da classificare);
2. l'elenco puntuale di `context_refs` e relativa portata;
3. una finestra della nota originale **solo come evidenza di disambiguazione**, chiaramente distinta dalla citazione da classificare;
4. `relations` rilevanti.

Output desiderato per ciascuna azione: `kind`, `intent`, `subject_owner`, `polarity`, `completion`, `rationale_evidence_refs` e `uncertain`; il formato concreto va definito e testato contro le regole Z e S2-V prima di integrarlo. **Non** passare direttamente l'output esteso a Z/S2-V assumendo che lo accettino: un adattatore esplicito e versionato può derivare un candidato legacy, ma deve registrare se ha perso informazioni. Se la nuova semantica richiede cambiare Z o S, costituisce un *ulteriore* esperimento, non lo stesso confronto isolato.

## 4. Guardrail non negoziabili

- **Fedeltà:** tutte le citazioni derivano dal testo, niente riscrittura, completamento inventato o fusione di parti non contigue.
- **Atomicità:** una proposta/task per azione; l'output finale può scegliere una sola azione secondo la politica esistente, ma deve conservare le altre per diagnosi.
- **Portata locale:** negazione, desiderio, citazione, completamento e autore dell'azione sono attribuiti a ciascuna azione, non alla nota in blocco.
- **Contesto condiviso verificabile:** `domani` può applicarsi a due azioni quando la frase lo supporta; la condivisione deve essere annotata, non inferita silenziosamente.
- **Ambiguità:** se la portata non è ricostruibile con evidenza, segnalare `ambiguous_scope` e non proporre in automatico.
- **Citazioni e parole di terzi:** una citazione riportata o un obbligo riferito esclusivamente a terzi non diventa un task dell'utente.
- **Sicurezza:** massimo un popup, sola proposta soggetta a conferma, nessuna scrittura reale; mantenere i controlli Z e i log di rifiuto.

## 5. Casi di accettazione derivati dalla diagnosi

| Caso | Requisito dell'interfaccia | Rischio già osservato |
|---|---|---|
| 001 / 006 | Azione e scadenza/luogo associati senza perdita | P0 perde dettagli |
| 004 | Telefonata rimane un task; il tempo non sostituisce l'azione | P1 escluso come `TEMPORAL_ONLY` |
| 017 | Modalità contrattuale riferita al fornitore | P0 propone attività di terzi |
| 019 / 024 | `magari` / `sarebbe bello` rimangono collegati all'azione | Falsi popup di desideri |
| 021 | `non ho deciso nulla` qualifica l'intenzione precedente | P1 perde la conclusione |
| 028 | Negazione solo su stampare; scaricare QR code rimane positivo | `NEGATED_CONTEXT` esteso |
| 030–033 | Azioni distinte, contesto temporale condiviso dove esplicito | P1 fonde più attività |
| 035–037 | Riferimenti ad autore, destinatario, anafore registrati, non riscritti | Frammenti incompleti / persi |

## 6. Criteri di decisione

Valutare **prima la correttezza del contratto**, poi la bontà del classificatore e infine i popup. Metriche separate: span verificati; azioni fuse/spezzate; contesti applicati al soggetto corretto; richiamo delle azioni presenti; precisione e falsi popup; A/P/E/U; regressioni gravi su negazione e desideri; perdita d'informazione nell'adattatore; costi/latency. Confronto appaiato, gold fuori dal runner. Non considerare le 40 note vecchie un holdout nuovo. Promuovere soltanto dopo un nuovo dataset sintetico non visto e, successivamente, note più realistiche con verifica umana.

## 7. Confine del prossimo esperimento

**Fase A (offline):** validare JSON e riferimenti, creare una scheda di audit manuale su 40 note già note. **Fase B (isolata):** usare le stesse estrazioni X2 congelate e confrontare (a) il percorso P1+C2 e (b) I1+C2-CTX, lasciando invariati modello, Z e S2-V *solo se l'adattatore legacy è esplicito e verificato*. Altrimenti limitare Fase B al solo confronto di classificazione e separare il test end-to-end. **Fase C:** freeze, nuovi casi indipendenti e verifica delle regressioni. Nel frattempo rimane candidata `X0+C2+Z+S2-V`.
