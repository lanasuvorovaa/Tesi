# Esperimento UC-01 — classificazione C2 vs C2-CTX (v01)

Questa è una **prova di classificazione appaiata**, NON un esperimento end-to-end sui popup. Le 40 note sintetiche e le estrazioni X2 v02 sono già conosciute. L'archivio NON incorpora il gold, non scrive attività o eventi e non modifica il prototipo.

## Preparazione macOS

1. Estrarre `esperimento_c2_ctx_uc01_v01.zip` sul **Desktop**.
2. Mantenere la cartella runtime `~/Desktop/confronto_slm_uc01_v01`, il modello `~/models/qwen3-1.7b-q4.gguf`, e non modificare il contenuto della cartella sperimentale.
3. Aprire Terminale ed eseguire:

```bash
cd "$HOME/Desktop/esperimento_c2_ctx_uc01_v01"
python3 test_c2_ctx.py
bash esegui_diagnostico.command
```

L'esecuzione produce due cartelle in `risultati/`: una con `interfaccia_I1.json` e flag offline, e una con `confronto_classificazioni.csv`, `dettagli/`, `report.json`, `manifest.json` e `llama_server.log`. **Inviare lo ZIP della cartella più recente `c2_ctx_...` contenente `confronto_classificazioni.csv`.** Se si interrompe, inviare anche il traceback del Terminale.

### Cosa verificare

- Si confrontano **le stesse azioni** per C2 e C2-CTX; nel runner cambiano il prompt e lo schema/output del classificatore, non l'estrazione.
- `kind` e `intent` restano comparabili, ma C2-CTX produce anche `subject_owner`, `polarity`, `completion`, `uncertain`.
- I `context_refs` sono riportati dalle estrazioni X2 e le loro citazioni vengono validate. La correttezza **semantica** delle portate non è dimostrata dal controllo strutturale: la classificazione finale richiede revisione manuale.
- Le relazioni X2 non vengono trasferite in questa prova; eventuali relazioni mancanti sono registrate nei flag.
- Non si invia il risultato di C2-CTX a Z/S2-V: la compatibilità downstream va affrontata con un adattatore valutato separatamente.

Nessuna etichetta gold viene inclusa nei prompt. Il parametro data/ora delle note è congelato nell'input. Il runtime usa il server locale, senza servizi cloud.
