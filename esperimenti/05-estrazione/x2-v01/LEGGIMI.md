# UC-01 — Esperimento diagnostico X0 / X1 / X2 v01

## Scopo

Confrontare l'estrazione originale X0, l'estrazione a citazioni estese X1 e la nuova **estrazione atomica con contesto X2**. Tutte ricevono le stesse note. C2, Z e S2-V rimangono byte-per-byte congelati. Lo ZIP include i componenti necessari, tranne il modello Qwen e il binario llama.cpp presenti sul Mac.

**Importante:** X2 cambia il formato di uscita dell'estrattore e introduce una proiezione verso citazioni letterali. Si tratta di un intervento composito nell'interfaccia di estrazione, non di un confronto tra soli prompt identici per schema. Non attribuire un eventuale miglioramento esclusivamente al prompt.

## Esecuzione sul Mac

1. Estrai lo ZIP sul Desktop in modo che esista `~/Desktop/esperimento_x2_atomico_uc01_v01/`.
2. Mantieni disponibile `~/Desktop/confronto_slm_uc01_v01/runtime/llama.cpp/build/bin/llama-server` e il modello `qwen3-1.7b-q4.gguf` nel percorso già utilizzato. **Non modificare** `selettore_s2_uc01_v01/`.
3. Terminale:

```bash
cd "$HOME/Desktop/esperimento_x2_atomico_uc01_v01"
python3 test_x2.py
bash esegui_diagnostico.command
```

Il confronto genera `risultati/x0_x1_x2_...` con `confronto_estrazioni.csv`, `confronto_candidati.csv`, `manifest.json`, `report.md`, `llama_server.log` e `dettagli/*.json`.

**Inviami lo ZIP della cartella `x0_x1_x2_...`**, compresi i `dettagli/`: servono per confrontare le estrazioni strutturate e gli errori di proiezione, non solo il numero dei popup.

## Come interpretare i risultati

- `x2_raw` conserva la risposta strutturata del modello.
- `x2_actions_accepted` contiene solo le azioni con citazioni e intervalli verificati contro la nota originale.
- `x2_validation_errors` indica gli elementi rifiutati; nessuna correzione silenziosa.
- `quote_validate` contiene le sole action_quote letterali passate a C2/Z.
- `popup_testo` è la citazione selezionata dal selettore congelato. **I contesti X2 non vengono aggiunti al popup**: la loro utilità deve essere misurata separatamente.

La prova sulle 40 note è **diagnostica**, poiché le note sono già state impiegate per progettare X2. Non è una conferma indipendente. Dopo la revisione qualitativa manuale serviranno freeze e nuovo testset prima di promuovere X2.

## Privacy e sicurezza

Non viene letto alcun gold; nessun accesso a calendari, task o note reali; nessuna scrittura applicativa. Il programma usa il modello locale e salva soltanto report e diagnostiche nella cartella dell'esperimento.
