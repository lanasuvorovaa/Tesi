# Protocollo di revisione C0 / C2

1. Controllare `manifest.json` e l'uguaglianza dell'estrazione X0; non rivedere le etichette gold a seconda delle predizioni di C2.
2. Usare `revisione_frammenti_compilata.csv` del 20 novembre come **riferimento provvisorio** sui 45 frammenti, ricordando che è annotazione ex post dell'assistente e non gold indipendente.
3. Calcolare **exact match** (`kind` e `intent`), accuratezza per singolo campo, correzioni C2 e regressioni rispetto a C0; documentare ogni caso di disaccordo.
4. Su ciascuna delle 24 note valutare non solo SI/NO popup, ma pertinenza, completezza, eventuale chiarimento necessario e casi di azioni multiple.
5. Tracciare attribuzioni diagnostiche separate: X0 (frammentazione), C (etichette), Z (gate sandbox), S (priorità e singola proposta); non attribuire causalità senza esperimento di ablazione.
6. **Criterio di non regressione prioritario:** non perdere i task di UC01-MAIN-097 e 118 e non produrre popup spuri su 076 e 113. Controllare anche 060, 062, 011, 022, 095.
7. Non modificare pipeline stabile X0+C0+Z+S in base ai soli conteggi. Successivo test su dati indipendenti, con decisioni e annotazioni congelate.
