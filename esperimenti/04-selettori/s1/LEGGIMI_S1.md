# Esperimento controllato S0 vs S1 — UC-01

## Ipotesi
Un controllo **deterministico e conservativo** dell’autonomia semantica dei frammenti, aggiunto a valle di S0, può eliminare falsi popup che provengono da un frammento connettivo («o Luca») o da un enunciato metadecisionale («devo ancora decidere»), senza togliere proposte corrette.

## Invarianti
Una sola esecuzione **X0 → C2 → Z** per nota; S0 e S1 ricevono **gli stessi candidati, etichette e decisioni di Z**. Non si modifica il prompt né il modello, il dataset, lo schema o il codice congelato di S0. S1 conserva i punteggi e i divieti di S0, aggiungendo tre motivi di veto generali e poi selezionando nuovamente il migliore fra i candidati ammessi. Nessuna scrittura in calendari o task.

## Procedura su Mac
1. Estrarre `selettore_s1_qwen3_uc01_v01` sul Desktop e lasciare `confronto_slm_uc01_v01` sul Desktop.
2. Conservare il modello in `~/models/qwen3-1.7b-q4.gguf`.
3. Dal Terminale:

```bash
cd "$HOME/Desktop/selettore_s1_qwen3_uc01_v01"
bash esegui.command
```

Caricare qui la cartella `risultati/s0_vs_s1_...` compressa in ZIP (include `dettagli`, CSV, report e manifest).

## Valutazione manuale **prima** della decisione
Per tutte le 24 note: classificare il suggerimento S0 e S1 in **corretto / errato / incompleto / nessuno atteso** e motivare l'esito. Per ogni candidato, verificare se S1 lo ha escluso per autonomia e se era effettivamente inadeguato. Contare veri falsi-popup rimossi, proposte valide perse, eventuali sostituzioni e omissioni ancora irrisolte. I due casi 076/113 sono esempi di sviluppo **non una misura indipendente**. Verificare che 060, 024, 097, 118 e gli altri popup utili siano preservati. Se un popup resta incompleto per X0 (es. 062), non attribuire automaticamente a S1 un problema che non modifica l'estrazione.

## Limiti
S1 è intenzionalmente minimale. Non unisce frammenti X0, non aggiunge nuove classi, non risolve la selezione multi-popup. A parità di candidati, un veto può rendere vuota la selezione: registrarlo anche se elimina un falso positivo. L'insieme di 24 note è usato per lo sviluppo; occorre poi una validazione held-out con annotazione preventiva.
