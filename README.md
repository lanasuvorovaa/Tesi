# Assistente AI locale per la gestione delle note — percorso di ricerca

Questo repository raccoglie il prototipo e i test che sto svolgendo per la mia tesi. L'obiettivo è realizzare un assistente AI che lavori **in locale** e riesca a riconoscere attività ed eventi all'interno di note scritte in linguaggio naturale, proponendoli all'utente senza creare automaticamente modifiche o appuntamenti.

## Come si è sviluppato il lavoro

**Sono partito dai primi test.** Ho preparato alcune note di esempio e iniziato a verificare come un modello linguistico di piccole dimensioni riconoscesse attività, appuntamenti e informazioni da non trasformare in promemoria. Questa fase mi ha aiutato a capire quali errori osservare e come organizzare i test.

**Poi mi sono fermato per sviluppare il prototipo.** Ho messo temporaneamente in pausa i confronti sperimentali per collegare i vari componenti in una demo funzionante: estrazione delle informazioni, classificazione, controlli e scelta delle proposte da mostrare. Il prototipo gira sul Mac con **Qwen3-1.7B** tramite **llama.cpp**.

**Una volta realizzata la demo, ho ripreso la ricerca sui modelli.** Alcuni errori non si risolvevano semplicemente modificando le istruzioni, quindi ho cercato alternative e confrontato in particolare **Qwen3-1.7B, Qwen3.5-2B e LFM2.5-1.2B**. Nei test svolti, Qwen3-1.7B è rimasto il riferimento per gli esperimenti successivi, pur con limiti ancora da risolvere.

**Sono quindi tornato ai test, un componente alla volta.** Ho confrontato diverse versioni dell'estrazione (**X**), della classificazione (**C**) e del selettore delle proposte (**S**). In seguito mi sono concentrato sul contesto: un modello può individuare un'azione ma perdere una data, una negazione oppure interpretare un desiderio o una citazione come un impegno reale.

**Negli esperimenti più recenti** ho provato a trasmettere separatamente al classificatore l'azione e il suo contesto (**I1**, **I1-R** e **C2-CTX**), controllando la qualità dei dati di ingresso e ripetendo le classificazioni sugli stessi input. Le risposte si sono dimostrate abbastanza stabili, ma alcuni errori di interpretazione sono rimasti.

## A che punto sono

La configurazione candidata del prototipo è attualmente:

`X0 → C2 → Z → S2-V`

- **X0:** estrae i possibili elementi utili dalla nota.
- **C2:** li classifica.
- **Z:** applica i controlli previsti dalla pipeline.
- **S2-V:** decide quali proposte possono essere mostrate.

Sto studiando una classificazione contestuale più semplice e rigorosa, senza sostituire la configurazione candidata prima di nuove verifiche. I risultati riportati finora sono **sperimentali**: molti test utilizzano note sintetiche già viste durante lo sviluppo e non equivalgono a una validazione indipendente.

## Materiali del repository

Il repository è pensato per contenere:

- `prototipo/` — il codice della demo locale, quando preparato per la pubblicazione;
- `esperimenti/` — un esperimento per cartella, con protocollo, script, dataset pubblicabili e risultati;
- `documentazione/` — sintesi e spiegazioni delle scelte tecniche.

Prima di caricare i materiali, verificherò di non includere dati personali, percorsi locali, file di modello `.gguf`, archivi duplicati o log con informazioni sensibili. Per leggere la storia dei test si potrà partire dai protocolli e dai report presenti nelle singole cartelle.

## Prossimi passi

Il prossimo lavoro è progettare e confrontare **C2-CTX v02**, mantenendo distinta la parte sperimentale dalla pipeline candidata. I miglioramenti dovranno poi essere controllati su nuove note non usate per progettare le modifiche.
