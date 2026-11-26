# Revisione C0 vs C2 — UC-01 / Qwen3-1.7B

## Perimetro e metodo

- 24 note del **development set** già utilizzate nello sviluppo del prompt. Non si tratta di una validazione indipendente.
- 45 frammenti di X0 condivisi fra le due configurazioni. Cambia esclusivamente il prompt C; X0, schema, Z, S, modello e parametri rimangono invariati.
- Gold label: **riutilizzate senza modifiche** le 45 annotazioni del confronto C0/C1 del 20 novembre 2026 per una comparazione coerente. Si considera corretto un frammento **solo se coincidono sia `kind` sia `intent`**.
- Le gold label riflettono scelte semantiche di annotazione e non una validazione da parte di revisori indipendenti. In particolare, 052 (EVENT vs TASK promemoria), 088 (TENTATIVE vs INFORMATIONAL per desiderio generico), 119 (comando playlist fuori UC-01) sono **casi da definire nel protocollo di annotazione** prima di valutare nuovi dati. Non sono state cambiate retroattivamente.

## Risultati per frammento

| Indicatore | C0 | C2 |
|---|---:|---:|
| Frammenti corretti (tipo + intenzione) | 17/45 (37.8%) | 22/45 (48.9%) |
| Frammenti errati | 28 | 23 |

- Correzioni C2 su errori C0: **10**.
- Regressioni C2 su casi corretti C0: **5**.
- Entrambe corrette: **12**; entrambe errate: **18**.
- Etichette modificate: **29/45**.

## Risultato sui popup e sulle note

- C0: **11/24** note con popup; C2: **14/24**. Aumento di **3**, non assimilabile a miglioramento dell'accuratezza.
- C2 migliore: **060** (mail prima omessa) e **024** (tutte le voci correttamente classificate, ma una sola suggerita).
- C0 migliore: **076** (falso popup «o Luca») e **113** (falso popup «devo ancora decidere»).
- Altri **20** casi hanno proposte equivalenti, con o senza limiti semantici o di copertura; i giudizi sono riportati nel CSV per nota.
- C2 conserva le proposte corrette **097** (invio del modulo) e **118** (controllo del preventivo), evitando le regressioni viste in C1.
- C2 resta più lento nell'esperimento: tempi logici medi del report di origine C0 **5,18 s** e C2 **6,57 s**. Non sono tempi di esecuzione sequenziale della doppia prova.

## Diagnosi della pipeline (attribuzione qualitativa, non causale)

- **X0:** frammenta informazioni collegate: 062 divide riunione e ora; 076 spezza l'incontro possibile, l'alternativa e il giorno; 002 separa finestra temporale e contatto. C non può ricostruire informazioni non presenti nel singolo frammento senza contesto aggiuntivo.
- **C2:** continua a interpretare male citazioni 022/095, ipotesi 028, doveri impliciti 062 e alcuni segnali di indecisione 113; 052 passa da EVENT a TASK e 094 riconosce NEGATED ma non TASK.
- **Z:** blocca appropriatamente i comandi citati 022/095, pur con etichette C errate; 060 porta finalmente a PROPOSE per la mail. In 076 la proposta su un complemento non autonomo resta un problema.
- **S:** propone un solo frammento anche in presenza di più azioni (024, 011, 062); seleziona frammenti non autosufficienti in 076 e 113 e perde data/ora della riunione in 062. La distinzione tra le responsabilità di X0, Z e S necessita test di ablazione o tracce aggiuntive.

## Decisione proposta

**Non sostituire ancora C0 con C2 nella pipeline stabile.** C2 recupera un task essenziale e migliora la classificazione di una lista, ma produce due nuovi falsi popup riconoscibili. C0 continua a essere la baseline stabile. Congelare la tabella di annotazione, definire un criterio di accettazione che privilegi la precisione dei popup e testare in modo mirato filtri di autonomia del frammento e coerenza semantica, senza modificare simultaneamente X0, C e S.

## Riproducibilità

Il report originale documenta Qwen3-1.7B Q4, CPU-only, `temperature=0`, `seed=42`, `max_tokens=350`, `context=4096`, con prompt C0 SHA-256 `8b736e2e127624cc36d41cd089a351f8b17f7be6e17cae060d39c346f3382432` e C2 SHA-256 `289a00ac6237e5adbdb44660e02e9f820e92774f0511f4f22b824ca21100534a`.
