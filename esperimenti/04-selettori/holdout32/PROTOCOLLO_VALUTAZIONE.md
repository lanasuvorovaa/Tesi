# Protocollo di valutazione pre-registrato

## Ipotesi
La configurazione candidata X0+C2+Z+S1 produce più popup semanticamente appropriati e meno falsi popup della baseline X0+C0+Z+S0, senza aumentare le omissioni di attività concrete.

## Unità di analisi
Una nota = una osservazione appaiata. 32 note sintetiche nuove; non confondere numero di candidati con numero di note. Contesti: task espliciti, eventi, completati, negazioni, testi riportati, ipotesi, informazioni, attività multiple e ambiguità temporali.

## Criteri primari
- **Corretto:** il popup (o l'assenza) è coerente con la nota e la policy; il frammento è autonomo e non travisa l'intenzione.
- **Falso popup:** propone contenuto che non è un'azione/evento effettivamente da gestire o che richiede informazioni essenziali non presenti senza segnalarlo.
- **Omissione:** non propone un'azione/evento sufficientemente espresso nella nota.
- **Parziale:** proposta pertinente ma incompleta (es. frammentazione data, solo una delle più attività; da annotare separatamente dal giudizio binario).
- **Da chiarire:** casi intenzionalmente ambigui, adjudication prima di attribuire correttezza.

## Procedura
1. Prima dell'inferenza, verificare le annotazioni del file gold, senza accedere agli output del modello; preservare l'hash della versione approvata.
2. Eseguire una sola prova, senza ritoccare il prompt o il selettore.
3. Valutare le proposte separatamente, idealmente con doppio annotatore che non conosca quale variante le ha prodotte. La mera presenza di popup non è successo.
4. Registrare per ogni nota `CORRETTA`, `FALSO_POPUP`, `OMISSIONE`, `PARZIALE`, `DA_CHIARIRE` e motivazione per entrambe le configurazioni.
5. Tabulare: successi per nota, falsi popup, omissioni, casi parziali, peggioramenti e miglioramenti appaiati, conservazione dei task positivi, tempi logici. Con 32 note, riportare conteggi e percentuali descrittive senza affermare significatività statistica.
6. Rilevare separatamente gli errori X0, C0/C2, Z, S0/S1; una diagnosi non equivale a identificazione causale senza ulteriore ablation.

## Limiti
Dataset sintetico costruito dopo gli esperimenti development, benché senza riutilizzare le 24 note. È un nuovo holdout ma non è una validazione esterna né una prova di prestazione real-world. I tre casi DA_VALUTARE vanno adjudicati prima del calcolo di una metrica binaria.
