# Protocollo UC-01 — X2 v02

La configurazione candidata rimane `X0+C2+Z+S2-V`. L’esperimento confronta X0, X1 e X2 v02 sulle 40 note sintetiche **già note**: è diagnostico, non validazione indipendente.

**Intervento X2 v02:** il modello restituisce azioni atomiche e citazioni contestuali letterali, senza offset. Python allinea le citazioni mediante corrispondenza esatta univoca, assegnando span `[inizio,fine)` Unicode secondo Python. Sono rifiutate citazioni assenti, ripetute in modo ambiguo, context invalidi, duplicati e relazioni non valide. Nessuna correzione fuzzy.

**Freeze:** C2, Z, S2-V, modello e parametri devono mantenere gli hash dei pacchetti precedenti. X0 e X1 non sono modificati. In X2 passano ai componenti frozen **solo le `action_quote`**; contesto e relazioni restano per la diagnosi e non sono concatenati nel popup. Non attribuire differenze al solo prompt: cambiano anche schema e validazione.

**Metriche:** completezza delle 40 note; azioni raw/accettate; motivi di rifiuto; atomicità; presenza di scadenze e negazioni nel contesto; esiti popup A/P/E/U a livello nota con revisione umana; regressioni rispetto a X0; latenza e chiamate. I numeri di popup non sono precision/recall.

**Decisione:** nessuna adozione di X2 a seguito di questa prova diagnostica. Se promettente, congelare e testare su nuove note annotate prima dell'inferenza.
