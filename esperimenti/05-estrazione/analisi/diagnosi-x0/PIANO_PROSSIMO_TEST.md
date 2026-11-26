# Piano prerequisiti per il prossimo esperimento

1. Conservare immutati gli output del test S2 e il registro delle decisioni.
2. Scegliere **una sola variabile sperimentale**: X0 con preservazione dei vincoli *oppure* ricomposizione del testo dopo S (non entrambe).
3. Definire prima del test uno schema gold per **azione/oggetto, destinatario, data/ora, luogo, referenti anaforici**, e distinguere esplicitamente i campi assenti dall’input.
4. Mettere a confronto la nuova variante con l’estrazione e la proposta originali su set diagnostico conosciuto, soltanto per debugging.
5. Congelare prompt, codice, soglie, hashes e metriche; poi provare su un nuovo set non utilizzato nella progettazione e riferire anche le regressioni.
6. Non cambiare classificatore C2, gate Z, selettore S2-V né vincolo di un popup per nota nello stesso esperimento.

**Limite:** non esiste ancora un pacchetto di inferenza per questa nuova ipotesi; questo documento è una specifica, non un test eseguito.
