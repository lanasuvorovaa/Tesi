# Protocollo X0 / X1 — completezza dell'estrazione

## Ipotesi e condizioni

H1: X1 aumenta la quota di proposte autosufficienti con azione, oggetto e vincoli preservati rispetto a X0, senza aumento sostanziale di falsi popup o citazioni respinte. X0+C2+Z+S2-V resta la candidata congelata; X1+C2+Z+S2-V è sperimentale.

L'unica variabile modificata è **il testo del prompt X**; modello, parametri, schema JSON, validatore, C2, Z, S2-V, dataset e criterio un popup sono identici. Entrambe le varianti elaborano ogni nota a partire da zero; non condividono frammenti perché proprio questi sono la variabile.

## Diagnostica su 40 note già conosciute

Verificare in modo esplorativo i casi 001,005,006,011,031,033,036,037; auditare comunque tutti i casi e le regressioni. Non scegliere nuove istruzioni di X1 dopo aver visto il test indipendente. Eventuali aggiustamenti dopo il replay diagnostico vanno documentati prima di congelare la versione da validare.

## Gold per nuovi casi (da definire prima di vedere output)

Per ciascuna nota: necessità di popup SI/NO/INCERTO; categoria TASK/EVENT; elenco di azioni valide, destinatario e vincoli temporali/luogo; indicatori `non_presente_nella_nota` distinti da `estratto_ma_perso`; accettabilità di una proposta con pronome/anàfora. Applicare A (corretto e autosufficiente), P (pertinente ma incompleto), E (errato/omesso), U (policy non definita). Gold tenuto separato e mai letto dal runner.

## Metriche e criteri

1. Validità estrattiva: quote raw, quote validate, quote rifiutate (per variante); errori JSON.
2. Esito per nota A/P/E/U, falsi popup, omissioni di opportunità, regressioni su casi corretti.
3. Copertura nel popup di azione/oggetto, luogo, tempo, destinatario, riferimenti contestuali, rispetto a ciò che è realmente contenuto nella nota.
4. Costo: numero chiamate, latenza logica e variabilità in numero di frammenti.
5. Per confronto appaiato: X1 migliora/peggiora/pari; includere anche cambi da corretto a parziale.

Preferire X1 solo con miglioramento coerente della completezza e nessuna regressione critica. Non inferire significatività da un numero ridotto di note e non utilizzare il set diagnostico come validazione di generalizzazione.

Rischi: X1 può produrre citazioni più lunghe ma peggiorare C2 o far perdere azioni multiple; eventuali errori di Z/S2-V rimangono separati; l'effetto del vincolo un-popup non è misurabile come recall completo delle attività.
