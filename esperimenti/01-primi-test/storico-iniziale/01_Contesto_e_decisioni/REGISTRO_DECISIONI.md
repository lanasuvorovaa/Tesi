# Registro decisioni

| Punto | Stato | Motivazione |
|---|---|---|
| Demo UC-01 v0.3, pipeline X0+C0+Z+S | Riferimento corrente | Non sostituita dagli esperimenti diagnostici |
| Qwen3-1.7B | Modello di riferimento | Confronti development favorevoli nel complesso; rimangono errori semantici |
| Qwen3.5-2B con X1 | Non adottato | Migliore segmentazione in alcuni casi ma esito end-to-end non superiore |
| LFM2.5-1.2B con C1 sperimentale | Non adottato | Confusione TASK/EVENT non risolta stabilmente |
| Qwen3-1.7B con classificazione C1 | **Sospeso in attesa di revisione** | Cambia 32 etichette su 45, ma presenta regressioni; 11 popup in entrambe le varianti |
| Modifiche alla pipeline / rifacimento dataset | Non decise | Prima completare revisione ed attribuzione degli errori |
| Validation indipendente | Da pianificare | Development noto non è test indipendente |
