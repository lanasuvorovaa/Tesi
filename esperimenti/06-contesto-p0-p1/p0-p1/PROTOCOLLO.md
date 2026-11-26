# UC-01 — Studio controllato dell'interfaccia X2 → C2 (v01)

## Ipotesi
Le regressioni X2 v02 dipendono in parte dalla proiezione atomica `action_quote`, che non trasferisce a C2 modalità, soggetto e dettagli contestuali. Una proiezione **letterale, contigua e delimitata** può migliorarne l'interpretazione mantenendo immutati C2, Z e S2-V.

## Variabile sperimentale
Si riutilizzano le **medesime azioni X2 accettate** del run `x0_x1_x2_20261124_233634.zip` (incluse nel file `estrazioni_x2_congelate.json`, identificabile tramite SHA-256). Nessuna nuova estrazione X2.

- **P0_ATOMICA**: trasmette soltanto la `action_quote` già validata.
- **P1_CLAUSOLA**: trasmette una porzione **contigua della nota originale** comprendente l'azione, limitata da punteggiatura, contrasti e — dove riconosciuti — altre azioni X2. Rimuove soltanto l'eventuale connettore avversativo iniziale. Non concatena frammenti distanti, non aggiunge date o parole, non corregge citazioni inventate.

Le quote entrano nel validatore X0 congelato e poi in C2, Z e S2-V senza modificare questi componenti. L'input a C2 cambia intenzionalmente; **non è un esperimento che modifica solo X**. Anche i segnali visibili a Z e al selettore possono cambiare in conseguenza delle nuove quote, pur mantenendo invariato il loro codice.

## Verifiche
1. Il primo controllo offline conferma che ogni output proiettato è una sottostringa esatta della nota, contiene l'azione originale e non oltrepassa un'altra azione riconosciuta in presenza di congiunzioni esplicite.
2. Sul Mac, lo stesso runtime Qwen3-1.7B Q4 esegue **solo le classificazioni C2**. Il confronto è appaiato per nota e per evidenza X2, con seed, temperatura e parametri fissati dal modulo congelato.
3. Per ciascuna nota annotare indipendentemente: popup SI/NO, testo, accuratezza A/P/E/U, falso popup, omissione e ragione. Isolare gli eventuali errori di proiezione, di classificazione e di filtro.
4. Distinguere miglioramenti dalla semplice crescita della lunghezza delle quote. Monitorare citazioni che includono attività di terzi, negazioni locali, citazioni, attività multiple e desideri non impegnativi.

## Limiti dichiarati
Il test riusa **le stesse 40 note sintetiche già osservate e le estrazioni X2 prodotte in precedenza**: è diagnostico e non indipendente. Le attività X2 scartate in precedenza non vengono recuperate dalla sola proiezione. La proiezione per clausole è una **euristica**, non un parser grammaticale certificato; può ancora perdere contesti condivisi tra azioni e inglobare elementi irrilevanti. La presenza delle parole nel testo non ne garantisce la correttezza semantica. L'uso del gold avviene esclusivamente nella revisione dopo le predizioni.

## Decisione
Non promuovere P1 solo perché aumenta il numero di popup o allunga le citazioni. Richiedere diminuzione delle omissioni e dei popup parziali senza nuovi falsi popup gravi; in presenza di risultati misti, mantenere X0+C2+Z+S2-V come candidata. Per sostenere un'adozione servirà una successiva validazione su note nuove.
