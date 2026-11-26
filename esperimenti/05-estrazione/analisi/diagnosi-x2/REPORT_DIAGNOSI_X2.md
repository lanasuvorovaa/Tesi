# UC-01 — Diagnosi dell'esperimento X0/X1/X2 (24 novembre 2026)

## Provenienza e stato

Origine: archivio `x0_x1_x2_20261124_231726.zip`, contenente 40 note e 120 righe di variante. Questa è una **diagnosi su note sintetiche già note**, non un holdout indipendente. Il runner registra C2, Z e S2-V congelati; X2 modifica struttura d'estrazione e proiezione. Non sono state eseguite nuove inferenze in questa analisi.

## Risultato quantitativo

| Misura | X0 | X1 | X2 |
|---|---:|---:|---:|
| Note | 40 | 40 | 40 |
| Citazioni validate | 55 | 37 | 0 |
| Popup prodotti | 21 | 18 | 0 |

X2: 66 azioni grezze su 40 note; 61 citazioni delle azioni letteralmente presenti, 5 non presenti; 0 span corretti e 66 scorretti. 74 elementi di contesto generati, dei quali 9 hanno citazioni non presenti nella nota. 2 output non oggetto JSON. Questi conteggi di presenza sono un controllo automatico letterale, **non** una valutazione della correttezza semantica.

## Diagnosi tecnica

1. Il validatore `x2_core.py` richiede `note[start:end] == action_quote` con indici Python 0-based, fine esclusa. La regola è coerente con la specifica. Nessuno degli span generati dal modello supera il controllo.
2. Esempio 001: la citazione `spedire` è presente nella nota, ma il modello restituisce `[10,14]` invece dell'intervallo corrispondente alla stringa. Lo stesso output inventa una seconda azione `inviare`, assente dalla nota.
3. La quantità elevata di citazioni presenti ma offset errati suggerisce che **il calcolo generativo delle posizioni** sia una barriera sistematica. Non la si risolve allentando il controllo di fedeltà.
4. Le citazioni non presenti (5 azioni) dimostrano anche errori di generazione. Recuperare gli offset programmaticamente può eliminare gli errori numerici **ma non** le citazioni allucinate, gli errori di segmentazione o la perdita del contesto nella proiezione a C2.
5. Inoltre il piano X2 passa a C2 soltanto `action_quote`. Anche dopo una correzione degli offset, un verbo isolato come `spedire` potrebbe risultare semanticamente insufficiente: va valutato separatamente dalla validità dello span.

## Decisione

**Non promuovere X2 v01.** L'esperimento è informativo per il debug, ma non permette ancora un confronto di accuratezza a valle: X2 non ha fornito alcun candidato valido a C2. Mantenere la candidata `X0+C2+Z+S2-V`.

## Correzione sperimentale raccomandata (X2 v02)

- Non chiedere più a Qwen di calcolare gli indici Unicode. Richiedere citazioni esatte, atomiche e relativi contesti come stringhe.
- Ricavare gli intervalli con un allineatore Python deterministico. Accettare solo sottostringhe letterali, con regole per occorrenze duplicate e ambiguità: nessuna correzione fuzzy e nessuna ricostruzione inventata.
- Rifiutare esplicitamente le citazioni non presenti e registrare il motivo; preservare i vincoli di contesto senza trasformarli in testo inventato.
- Testare in isolamento l'allineatore su esempi artificiali con offset verificabili, negazioni, più azioni e ripetizioni.
- Eseguire prima un **replay offline** delle azioni grezze esistenti per misurare quante citazioni diventano validabili; questo replay non sarà un nuovo risultato inferenziale e non dimostrerà correttezza dei popup.
- Soltanto dopo, congelare prompt/runner X2 v02, confrontarlo sulle 40 note conosciute (diagnostica) e verificarlo su nuove note indipendenti, senza modificare C2/Z/S2-V.

## Integrità interpretativa

Non indicare 0 popup di X2 come prova di migliore filtraggio dei falsi positivi. Non chiamare le 66 azioni «corrette»: 61 sono citazioni letteralmente presenti ma la loro opportunità semantica resta da giudicare. Non attribuire a C2, Z o S2-V errori avvenuti prima della loro esecuzione.
