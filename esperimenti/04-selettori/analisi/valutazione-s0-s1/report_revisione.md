# Valutazione manuale S0 vs S1 — UC-01

**Data:** 20 novembre 2026  
**Disegno:** development set di 24 note; stessi 45 candidati prodotti una volta da X0+C2+Z; unica variazione selettore S. Non è validazione indipendente.

## Risultato

| Metrica | S0 | S1 |
|---|---:|---:|
| Note | 24 | 24 |
| Candidati | 45 | 45 |
| Popup | 14 | 12 |
| Falsi popup noti (076, 113) | 2 | 0 |
| Popup validi precedentemente selezionati e rimossi | — | 0 |

Le sole selezioni cambiate sono UC01-MAIN-076 (`o Luca` → nessun popup) e UC01-MAIN-113 (`devo ancora decidere` → nessun popup). Entrambe le rimozioni sono giustificate semanticamente. Le altre 22 note mantengono esattamente la stessa selezione. La conclusione riguarda i popup osservati, non la capacità di generalizzazione del filtro né la correttezza di ogni classificazione C2.

## Diagnosi separata per componente

- **S1:** i nuovi veti impediscono un'alternativa nominale isolata e una metadescrizione di indecisione. Non sono state osservate regressioni nelle 24 note.
- **X0:** persistono frammentazioni che separano l'evento dal suo tempo (002, 062) o spezzano un'alternativa (076); S1 evita la proposta sbagliata ma non ricostruisce il significato completo.
- **C2:** classifica erroneamente come evento `o Luca` e come task impegnato `devo ancora decidere`; il filtro successivo ne contiene l'effetto, senza correggere la classificazione. In 062 non riconosce la preparazione delle slide come attività autonoma.
- **Z:** conserva il blocco dei testi citati (022, 095), delle negazioni e dei completati; non sono emerse modifiche attribuibili a Z.
- **Selezione singola:** in 011 manca la seconda attività preliminare; in 024 vengono riconosciute tre attività ma se ne propone una sola. S1 non risolve questa limitazione.
- **Temporalità:** in 052 `prossimo fine settimana` richiede chiarimento/normalizzazione prima di un'integrazione automatica nel calendario.

## Interpretazione e decisione

**Esito positivo sul development set per l'ipotesi ristretta:** due falsi popup eliminati, nessuna proposta precedentemente conservata persa. È opportuno mantenere la pipeline stabile invariata e **candidare X0+C2+Z+S1 a una validazione indipendente**, con note nuove e criteri di valutazione definiti prima di vedere le predizioni. Non aggiungere altre regole su questo stesso set senza separare un nuovo test.

**Metriche da raccogliere nella validazione:** precisione dei popup, recall delle attività/eventi attesi, falsi popup per nota, omissioni per selezione singola, correttezza/completezza temporale, confronto appaiato S0–S1. Separare errori X0, C2, Z e S; distinguere `CLARIFY` da `PROPOSE`.

## Riproducibilità

Manifest associato all'esperimento: dataset SHA-256 `4724c163e7357246b1ae52a1e17a575d293e2cf9bf438a3ef394c2b2512e5543`; prompt C2 SHA-256 `289a00ac6237e5adbdb44660e02e9f820e92774f0511f4f22b824ca21100534a`. Parametri del modello: temperatura 0, seed 42, massimo 350 token, contesto 4096, CPU-only. I file di revisione sono giudizi manuali interpretativi e non sostituiscono una seconda annotazione indipendente.
