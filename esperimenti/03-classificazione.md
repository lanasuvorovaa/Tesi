# 03 — Classificazione: C0 contro C1 e C0 contro C2

## Da dove nasce l'idea

Dopo il confronto tra modelli (esperimento 02) ho tenuto Qwen3-1.7B e ho cercato di migliorare un componente alla volta. Ho iniziato dal classificatore C, perché nelle prime prove molti errori erano etichette sbagliate: le slide da preparare etichettate FACT/COMPLETED, la mail di 060 etichettata FACT e quindi persa, le attività del trasloco in 024 classificate come FACT o EVENT.

La domanda era: se cambio solo il prompt di classificazione, lasciando identico tutto il resto, le etichette migliorano senza creare nuovi popup sbagliati?

## Cosa ho fatto

Modello Qwen3-1.7B Q4 in locale con llama.cpp, solo CPU, temperatura 0, seed 42, massimo 350 token, contesto 4096, JSON vincolato. Dataset: le 24 note del development set. Ogni nota viene estratta una sola volta con X0 e gli stessi 45 frammenti vengono classificati da entrambe le varianti. Z e S sono invariati. Cambia solo il testo del prompt di sistema di C.

- **C1:** aggiunge definizioni e contrasti per distinguere azioni anche impersonali («il documento va consegnato»), appuntamenti fissati, azioni concluse, negate, ipotetiche o solo desiderate, informazioni e citazioni. Introduce le intenzioni `NEGATED` e `HYPOTHETICAL`.
- **C2:** l'ho scritto dopo la revisione di C1, per correggerne le regressioni senza perdere i task che C0 trovava. Tra le regole: un'azione passata resta TASK. Una data, un nome o un'alternativa isolati non sono da soli TASK o EVENT. Il tempo futuro non implica `COMPLETED`.

Per valutare ho annotato a mano, per ciascuno dei 45 frammenti, il tipo e l'intenzione attesi nel contesto della nota completa. Alcune scelte di annotazione: le azioni concluse restano TASK/COMPLETED, le frasi citate sono `INFORMATIONAL`, i complementi isolati (date, nomi, pezzi di frase) sono FACT/INFORMATIONAL. Un frammento è corretto solo se coincidono sia tipo sia intenzione. Per il confronto C0/C2 ho riusato le stesse annotazioni senza modificarle. Ho poi giudicato ogni nota confrontando i popup delle due varianti.

## Cosa si vede

**Per frammento (45 frammenti).**

| Misura | C0 | C1 | C2 |
|---|---:|---:|---:|
| Tipo e intenzione corretti | 17 (37,8%) | 18 (40,0%) | 22 (48,9%) |
| Solo tipo corretto | 28 | 24 | 32 |
| Solo intenzione corretta | 21 | 25 | 27 |
| Errori di C0 corretti | – | 8 | 10 |
| Corretti di C0 peggiorati | – | 7 | 5 |
| Etichette cambiate rispetto a C0 | – | 32 | 29 |

Le etichette di C0 sono identiche nelle due esecuzioni.

**Per nota (24 note).** I popup sono 11 per C0 e 11 per C1, 14 per C2. I tempi medi logici sono 4,01 s (C0) contro 4,81 s (C1) nella prima prova e 5,18 s (C0) contro 6,57 s (C2) nella seconda. Sono ricostruiti da X0 condivisa più la classificazione, non sono tempi di esecuzione reali.

| Giudizio sulla nota | C0 vs C1 | C0 vs C2 |
|---|---:|---:|
| Variante migliore | 0 | 2 (060, 024 con limite) |
| C0 migliore | 5 | 2 (076, 113) |
| Parità | 11 | 11 |
| Parità con limite | 7 | 9 |
| Parità errata | 1 | 0 |

C1 corregge alcuni frammenti, ma perde due task reali e aggiunge due falsi popup: in 097 «Entro venerdì devo inviare il modulo di iscrizione» diventa FACT e non viene proposto. In 118 «domani devo controllarlo» diventa COMPLETED. In 076 propone «o Luca» e in 113 «devo ancora decidere».

C2 recupera la mail di 060 (la chiamata diventa TASK/NEGATED e «devo invece scrivergli una mail» TASK/COMMITTED, con popup corretto) e in 024 riconosce tutte e tre le attività del trasloco, anche se il selettore ne propone una sola. Mantiene i task di 097 e 118. Restano però i falsi popup «o Luca» (076) e «devo ancora decidere» (113, come TASK/COMMITTED). Inoltre C2 continua a trattare come impegni reali i comandi citati di 022 e 095 (il popup non compare solo perché Z li blocca), sbaglia l'ipotesi di 028 e in 052 passa da EVENT a TASK.

Alcuni problemi non dipendono da C: X0 separa la riunione dal suo orario (062), spezza «Potrei incontrare Andrea o Luca venerdì» in quattro pezzi (076) e separa la finestra temporale dal contatto (002). S propone un solo frammento anche quando le attività sono più di una (011, 024, 062).

## Cosa ne concludo

C1 non l'ho adottato: il miglioramento da 17/45 a 18/45 è troppo piccolo e le regressioni su 097, 118, 076 e 113 sono più gravi dei frammenti corretti. C2 va meglio (22/45, 5 regressioni) e non ripete le perdite di 097 e 118, ma introduce due falsi popup riconoscibili. Per questo non ho sostituito C0 nella pipeline stabile: ho tenuto C2 come classificatore candidato e sono passata a lavorare sul selettore, perché i due falsi popup rimasti nascevano da frammenti non autonomi che S lasciava passare (esperimento 04).

Limiti: le 24 note hanno guidato la scrittura di C1 e C2, quindi questo è un test di sviluppo e non una validazione indipendente. Le etichette attese sono una revisione preliminare assistita, fatta dopo aver visto le predizioni, senza annotatori indipendenti, e alcune convenzioni sono ancora da fissare nel protocollo (052 evento o promemoria, 088 desiderio TENTATIVE o INFORMATIONAL, 119 comando fuori dominio). L'attribuzione degli errori a X0, C, Z o S è qualitativa, non misurata con test di ablazione. I test sul solo classificatore non misurano direttamente la qualità dei popup finali.

## Dati

`03-classificazione-dati.csv` (90 righe = 45 frammenti × 2 prove): `prova` è `C0_vs_C1` o `C0_vs_C2`. `tipo_atteso` e `intenzione_attesa` sono le etichette attese della revisione preliminare. Per C0 e per la variante (`variante` = C1 o C2, colonne `var_…`) ci sono tipo, intenzione, `…_corretta` (SI se entrambi coincidono con l'atteso), decisione di Z (`PROPOSE`, `CLARIFY`, `BLOCKED`) e `…_scelto` (SI se è il frammento proposto come popup). `commento` spiega l'annotazione. `esito_nota` è il giudizio sull'intera nota (C0 migliore, Parità, Parità con limite, ecc.), ripetuto su ogni frammento della nota.
