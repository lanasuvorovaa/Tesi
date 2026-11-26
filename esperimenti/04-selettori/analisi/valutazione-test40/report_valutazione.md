# Valutazione comparativa S1 / S2-V / S2-R / S2-VR — 40 note

## Integrità e metodo

- Archivio esaminato: `nuove_note_20261122_192516.zip`.
- Sono presenti **40 note distinte**, **220 righe di candidati** e dettagli per tutti i 40 ID.
- Il test è un holdout **sintetico**, nuovo rispetto ai precedenti set diagnostici, non una prova su dati reali.
- La configurazione comune resta X0+C2+Z; differisce soltanto il selettore.
- Gold utilizzato: `gold_test40_PREDEFINITO(1).csv`, ancora **PREDEFINITO_DA_CONFERMARE**. In particolare 029 è `DA_VALUTARE`.
- Valutazione interpretativa motivata: A = corretto/autonomo o corretta non-proposta; P = proposta pertinente ma incompleta; E = errato/omesso; U = policy non risolta.

## Risultati

| Variante | A | P | E | U | Popup |
|---|---:|---:|---:|---:|---:|
| S1 | 23 | 7 | 9 | 1 | 22 |
| S2-V | 24 | 7 | 8 | 1 | 21 |
| S2-R | 23 | 7 | 9 | 1 | 22 |
| S2-VR | 24 | 7 | 8 | 1 | 21 |

Le varianti producono **lo stesso output su 39/40 note**. L'unica variazione è UC01-S2TEST-019: S1 e S2-R propongono «Magari un giorno imparerò a suonare il violoncello», S2-V e S2-VR non propongono alcun popup (coerente con il gold NO). Non sono osservate nuove regressioni rispetto a S1, ma il guadagno è **un solo caso**.

## Errori comuni che restano

- **Omissioni**: 004, 005, 011, 028. La causa precisa va verificata nelle tracce X0/C2/Z/S; non attribuire automaticamente ogni omissione a S.
- **Falsi popup**: 013, 014 (azioni/stati di terzi); 021, 024 (intenzioni vaghe).
- **Popup parziali o contestualmente dipendenti**: 001, 006, 031, 032, 033, 036, 037.
- **Multiattività**: 030 propone una delle tre attività, coerentemente con il protocollo di un solo popup, ma non misura il recupero di tutte le azioni.

## Caso 029 e decisione

«Non è necessario comprare la batteria; va invece controllato il caricatore.» Non appare alcun popup per nessuna variante. Il gold allegato reca `DA_VALUTARE`: prima di calcolare un'accuratezza definitiva è necessario approvare la regola sugli obblighi impersonali. La conversazione precedente conteneva una proposta di includerli, ma non una conferma esplicita dell'utente. Se la policy è **SI**, il 029 sarà un'omissione per tutte; se **NO**, sarà una corretta non-proposta per tutte. **La graduatoria tra selettori non cambia.**

## Decisione sperimentale proposta

**Preferire provvisoriamente S2-V** tra i selettori testati: elimina un falso positivo in più di S1 sul set nuovo, senza peggioramenti osservati, e non richiede il ranking S2-R che qui non ha prodotto beneficio. S2-VR è equivalente a S2-V su queste 40 note, ma combina due interventi e dunque aggiunge complessità non giustificata da un vantaggio misurato.

L'evidenza è limitata: 1 caso di guadagno su 40, valutazione sintetica, gold con policy irrisolta. **Non interpretare la differenza come superiorità statisticamente dimostrata né validità in produzione.** Registrare la scelta come *candidata sperimentale*, mantenendo S1 come riferimento riproducibile, prima di ulteriori test reali o su nuovi dati.

## File

- `revisione_160_valutazioni.csv`: 40 × 4 valutazioni con motivazione.
- `sintesi_40_note.csv`: confronto per nota.
- `confronto_note_originale.csv` e `confronto_candidati_originale.csv`: output non modificati della prova.
