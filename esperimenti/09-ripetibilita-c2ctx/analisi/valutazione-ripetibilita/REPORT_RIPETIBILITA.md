# Analisi di ripetibilità C2-CTX v01 — 25 novembre 2026

## Metodo
20 azioni I1-R congelate, tre inferenze per azione (60 richieste), stessi input e parametri del modello. Z e S2-V non eseguiti. Dataset sintetico conosciuto: test di ripetibilità, non di accuratezza né validazione su nuovi dati.

## Esito verificato
- 60/60 risposte formalmente valide.
- 19/20 azioni identiche nei sei campi (`kind`, `intent`, `subject_owner`, `polarity`, `completion`, `uncertain`), pari al 95% delle azioni; le tre ripetizioni per ciascuna azione hanno lo stesso hash input.
- Unica azione instabile: `UC01-S2TEST-026/a1`. `intent` è `COMPLETED` nel round 1 e 3, `COMMITTED` nel round 2; `completion=DONE` in tutte e tre.
- Nessuna variazione nei campi `kind`, `subject_owner`, `polarity`, `completion`, `uncertain`.
- `subject_owner=SELF` per tutte le 60 risposte; non è evidenza che i soggetti siano stati individuati correttamente.

## Interpretazione
La variabilità su input identici è limitata, ma non assente. Restano errori semantici ripetuti: l'evento oculistico (008) reso TASK, l'azione del fornitore (017) attribuita a SELF, il desiderio (020) reso COMMITTED, la citazione narrativa (038) interpretata come TASK personale. La stabilità non garantisce accuratezza.

## Decisione metodologica
Conservare X0+C2+Z+S2-V come configurazione candidata. Progettare una variante C2-CTX v02 come nuovo classificatore sperimentale, con schema di output più semplice e distinzioni esplicite tra evento/task/fatto, autore, citazione, negazione e stato dell'azione. Congelare prima prompt, esempi e criteri; confrontare sul dataset noto solo diagnostically, quindi validare su note nuove. Non presentare la ripetibilità come dimostrazione di superiorità. 
