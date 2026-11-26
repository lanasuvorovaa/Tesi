# Protocollo diagnostico C2 vs C2-CTX, v01

## Ipotesi
Le etichette di una singola azione atomica possono migliorare quando il classificatore riceve esplicitamente citazione, qualificatori e loro associazione, invece di fare affidamento sulla sola stringa atomica e sulla nota originale.

## Variabile sperimentale
C2 (prompt congelato, restituisce due etichette) vs C2-CTX (nuovo prompt e nuovo output strutturato). Stesso modello Qwen3-1.7B, parametri di campionamento, note sintetiche conosciute e azioni X2 v02 con hash congelati. I nuovi campi della risposta implicano che si testa una **nuova interfaccia di classificazione**, non una modifica unicamente del prompt.

## Primo limite della prova
Non si può dichiarare l'effetto sul popup: Z e S2-V **non** vengono eseguiti. Un futuro adattatore versionato sarà necessario per mappare le nuove proprietà semantiche su candidati legacy, e tale mappatura potrebbe perdere contesto. Il primo run deve pertanto restare a livello di classificazione.

## Contratto e provenienza
Si ricostruisce I1 da `estrazioni_x2_congelate.json`. Si controlla che ogni azione e contesto siano citazioni esatte e abbiano span coerenti. La portata della citazione associata da X2 è attribuita esplicitamente solo all'azione corrispondente. Questa associazione **non è gold** e non viene spacciata per verifica semantica. I componenti preesistenti sono controllati con FREEZE_S2.json. Il nuovo prompt e il runner sono registrati con SHA256 nel manifest.

## Metriche e revisione
- Frazione di risposte conformi allo schema su ciascun ramo, tempi per azione.
- Accuratezza `kind` e `intent` per azione valutata manualmente, con note di ambiguità.
- Per C2-CTX: verifica umana dei campi `subject_owner`, `polarity`, `completion`, `uncertain`.
- Differenze appaiate caso-per-caso e rischi su negazioni, desideri, terzi, citazioni, eventi e multi-azione.
- Errori dell'estrattore e del contratto devono essere separati dagli errori della classificazione.

## Decisione
Nessuna adozione di C2-CTX da questa sola diagnosi: servono una revisione umana, un test end-to-end con adattatore esplicito che non aggiri Z, e infine un nuovo dataset indipendente. La candidata storica resta `X0+C2+Z+S2-V`.
