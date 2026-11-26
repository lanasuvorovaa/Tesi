# UC-01 — Esperimento X2 v02

## Stato
Correzione dell’errore sistematico di span numerici osservato in X2 v01. Il modello non produce più offset; l'allineatore Python cerca citazioni esatte e univoche. C2, Z, S2-V e X0/X1 restano congelati.

## Sul Mac
1. Estrai questa cartella sul Desktop; mantieni `~/Desktop/confronto_slm_uc01_v01` e il modello Qwen originali.
2. Apri Terminale:

```bash
cd "$HOME/Desktop/esperimento_x2_atomico_uc01_v02"
python3 test_x2.py
bash esegui_diagnostico.command
```

3. Comprimi e allega tutta la nuova cartella `risultati/x0_x1_x2_...` con `dettagli/`, `confronto_estrazioni.csv`, `confronto_candidati.csv`, `manifest.json` e `report.md`.

## Risultato offline incluso
`replay_offline/`: prova sul precedente output X2 v01, senza inferenza; 44 di 66 azioni accettate dal validatore stretto v02. Non è evidenza sull'accuratezza di X2 v02. L’input originale del replay non è incluso in questo ZIP; il replay è riproducibile passando lo ZIP originale: `python3 replay_offline_v01.py --zip /percorso/x0_x1_x2_20261124_231726.zip`.

## Importante
La nuova variante X2 resta diagnostica; i metadati context non raggiungono C2/Z e possono quindi essere persi nel popup. Il gold non è letto dal runner e non vengono scritti calendari o task.
