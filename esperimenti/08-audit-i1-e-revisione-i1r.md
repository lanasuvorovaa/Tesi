# 08 — Audit dei dati I1 e revisione del contesto (I1 contro I1-R)

## Da dove nasce l'idea

Nell'esperimento 07 C2-CTX v01 aveva trasformato quasi tutti gli eventi in task, attribuito SELF a tutte le 39 azioni e ignorato negazioni, desideri e citazioni. Guardando gli input, però, mi ero accorta che anche i contesti passati al classificatore non erano sempre corretti. Prima di scrivere un nuovo prompt volevo capire se gli errori dipendessero dal modello o da dati già rappresentati male.

L'esperimento ha due parti:

1. un **audit** dei riferimenti contestuali di I1, senza nuove inferenze;
2. una **prova appaiata** in cui correggo a mano i contesti di alcune azioni (I1-R) e li passo allo stesso C2-CTX v01, per vedere se cambiano le classificazioni.

## Cosa ho fatto

**Audit.** Ho ripreso l'interfaccia I1 dell'esperimento 07: 40 note, 39 azioni validate da X2 (in 31 note), 50 riferimenti contestuali e nessuna relazione tra azioni. Per ogni riferimento ho controllato prima la parte strutturale (lo span restituisce esattamente il testo? la portata indica un'azione esistente?) e poi, con una revisione manuale preliminare, se il ruolo assegnato avesse senso. Ho usato tre esiti: `OK`, `ROLE_MISMATCH` (ruolo non coerente con il testo) e `OVERBROAD` (citazione troppo estesa).

**I1-R.** Ho corretto i contesti di **18 azioni in 12 note** (008, 017, 019, 020, 021, 025, 026, 028, 030, 034, 038, 039), scelte tra i casi dove l'audit e l'esperimento 07 mostravano i problemi più evidenti. Ho aggiunto ruoli che prima mancavano, come `modality` per «Mi piacerebbe» o «è confermata», e spostato riferimenti finiti sul ruolo sbagliato. Le citazioni restano esatte e gli span sono calcolati in Python. Tutto il resto è rimasto invariato: le 39 azioni X2, gli ID, il testo delle note, il prompt e lo schema di C2-CTX v01, il modello Qwen3-1.7B e i parametri (`temperature=0`, `seed=42`, `max_tokens=350`). Le altre 21 azioni hanno input identico e fanno da controllo. In totale sono 78 inferenze (39 con I1 e 39 con I1-R). Z e S2-V non sono stati eseguiti.

Alcuni problemi non si potevano correggere solo con il contesto e li ho lasciati come erano: in 008 la seconda «azione» è un frammento temporale, in 021 «non ho deciso nulla» è trattata come azione, e in 028 l'azione negata («Non devo stampare i biglietti») era già stata scartata da X2.

## Cosa si vede

**Audit.** Tutti i 50 riferimenti superano il controllo strutturale: span esatti e portata coerente. Dal punto di vista del significato, invece, la situazione è diversa:

| Esito della revisione preliminare | Riferimenti |
|---|---:|
| OK | 16 |
| ROLE_MISMATCH | 29 |
| OVERBROAD | 5 |
| Totale | 50 |

I ruoli usati sono solo quattro: `time` (24), `recipient` (18), `place` (5) e `condition` (3). Non compaiono mai `polarity`, `modality`, `completion`, `speaker`, `discourse` o `antecedent`. Il classificatore quindi non riceveva in forma esplicita proprio le informazioni su negazioni, desideri e soggetti. Qualche esempio:

- in 006 il verbo «caricare» è etichettato come `time`;
- in 010 «il 12 dicembre alle 8» è etichettato come `place` e come `recipient`;
- in 020 «Mi piacerebbe» è etichettato come `time`;
- in 025 «ci pensa già Alessia» è un `recipient`, e non viene registrato che l'azione è di un'altra persona.

L'adattatore aveva inoltre segnalato 17 perdite: 16 ruoli `object_reference` non supportati e la relazione `after` della nota 026, presente in X2 ma non trasferita.

**I1 contro I1-R.** Tutte le 78 risposte sono valide. Il risultato principale è che **35 azioni su 39 hanno le sei uscite identiche** (`kind`, `intent`, `subject_owner`, `polarity`, `completion`, `uncertain`). Solo quattro azioni cambiano almeno un campo:

| Azione | Cosa cambia da I1 a I1-R | Lettura |
|---|---|---|
| 011-a1 «è fissata la prova dell'orchestra» | completion PENDING → DONE, uncertain True → False | input identico: non può dipendere dalla revisione |
| 026-a1 «Ho disdetto la visita» | intent COMMITTED → COMPLETED | miglioramento plausibile |
| 028-a1 «devo scaricare il QR code» | intent COMMITTED → TENTATIVE, completion DONE → PENDING, uncertain False → True | misto; polarity resta NEGATIVE |
| 039-a1 «prenota una stanza» | intent COMMITTED → TENTATIVE, polarity POSITIVE → UNCLEAR, completion DONE → PENDING, uncertain False → True | meno assertivo, ma resta un TASK di SELF |

`kind` e `subject_owner` non cambiano mai: TASK 38 / EVENT 1 e SELF 39/39 in entrambe le condizioni. Restano quindi gli errori più importanti. La visita oculistica (008) e l'incontro del gruppo di lettura (034) restano TASK. Il fornitore di «Il contratto prevede che il fornitore invii un rapporto mensile» (017) e Alessia (025) restano SELF. «Mi piacerebbe aprire un laboratorio di ceramica» (020) resta COMMITTED anche con «Mi piacerebbe» marcato come `modality`. La frase del romanzo (038) resta TASK/COMMITTED/SELF/DONE.

## Cosa ne concludo

Correggere i dati di ingresso, da solo, non basta. I1-R rappresenta meglio ruoli e portate, ma C2-CTX v01 sembra quasi ignorarli: non migliora la distinzione tra eventi e task né l'attribuzione del soggetto. Il classificatore contestuale resta non adottato e la configurazione candidata resta `X0 → C2 → Z → S2-V`.

Il caso 011-a1 mi ha fatto fermare: la classificazione è cambiata con un input identico. Non posso attribuire a I1-R differenze che potrebbero dipendere dalla variabilità del modello, quindi prima di progettare un nuovo classificatore ho deciso di misurare la ripetibilità (esperimento 09).

Limiti: le correzioni di I1-R sono annotazioni manuali, fatte da me su note sintetiche che conosco già, quindi sono un intervento diagnostico e non un gold indipendente. Anche gli esiti dell'audit sono giudizi preliminari. Non ho misurato i popup.

## Dati

`08-audit-i1-e-revisione-i1r-dati.csv` unisce le due parti. La colonna `prova` vale `audit_I1` (50 righe, una per riferimento contestuale) oppure `I1_vs_I1R` (39 righe, una per azione). Per l'audit: `contesto` e `ruolo_attuale` sono il riferimento e il ruolo assegnati da I1, `span_esatto` e `scope_strutturale` sono i controlli formali, `audit_semantico` (OK, ROLE_MISMATCH, OVERBROAD) e `nota_audit` sono il giudizio della revisione preliminare. Per il confronto: `contesti_modificati` indica le 18 azioni corrette, `contesti_I1` e `contesti_I1R` sono i due input in JSON, le colonne `*__I1` e `*__I1R` sono le sei uscite di C2-CTX nelle due condizioni, `campi_cambiati` e `commento` riassumono le differenze. `caso`, `azione_id`, `nota` e `azione` sono comuni alle due parti.
