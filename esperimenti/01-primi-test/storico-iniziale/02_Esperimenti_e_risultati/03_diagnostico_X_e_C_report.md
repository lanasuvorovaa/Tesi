# Diagnostico mirato UC-01 — X di Qwen3.5, C di LFM2.5

**Dati:** development, 10 note. Non validation indipendente.
**Configurazione:** temperatura 0, seed 42, max_tokens 350, schema JSON vincolato, server locale CPU.
**Nota:** le varianti sono ipotesi una tantum. Non sono nuove versioni del prototipo.

## LFM2.5-1.2B: C originale vs C sperimentale

Per ogni nota, i due classificatori ricevono **gli stessi frammenti X0**, estratti una sola volta.
Z e selettore originali vengono rieseguiti su entrambi gli insiemi di classificazioni.
Un popup non equivale a classificazione corretta.

| Caso | Frammento | C0: tipo / intenzione | C1: tipo / intenzione |
|---|---|---|---|
| RIUNIONE-00 | La riunione con Chiara è fissata alle 9 di martedì | TASK/COMMITTED | EVENT/COMMITTED |
| RIUNIONE-00 | le slide devono essere pronte prima | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-01 | Martedì alle 9 ho una riunione con Chiara | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-01 | devo preparare le slide prima | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-02 | Devo finire le slide prima della riunione con Chiara | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-02 | prevista per martedì alle 9 | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-03 | Per martedì alle 9 è fissata la riunione con Chiara | TASK/COMMITTED | EVENT/COMMITTED |
| RIUNIONE-03 | Le slide vanno preparate prima | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-04 | Martedì alle 9 vedrò Chiara in riunione | TASK/COMMITTED | EVENT/COMMITTED |
| RIUNIONE-04 | Prima devo completare le slide | TASK/COMMITTED | TASK/COMMITTED |
| RIUNIONE-05 | La riunione con Chiara sarà martedì | TASK/COMMITTED | EVENT/COMMITTED |
| RIUNIONE-05 | devo avere le slide pronte | TASK/COMMITTED | TASK/COMMITTED |
| UC01-MAIN-019 | Ieri ho restituito le chiavi | TASK/COMMITTED | TASK/COMMITTED |
| UC01-MAIN-019 | Domani devo prenotare il furgone | TASK/COMMITTED | TASK/COMMITTED |
| UC01-MAIN-022 | Domani cancello ogni appuntamento | TASK/COMMITTED | TASK/COMMITTED |
| UC01-MAIN-052 | Ricordarmi la visita di controllo il prossimo fine settimana. | TASK/COMMITTED | TASK/COMMITTED |
| UC01-MAIN-060 | Non devo più chiamare il fornitore | TASK/COMMITTED | TASK/COMMITTED |
| UC01-MAIN-060 | devo invece scrivergli una mail | TASK/COMMITTED | TASK/COMMITTED |

## Qwen3.5-2B: X originale vs X sperimentale

Questa prova si ferma all’estrazione X, quindi non può stabilire se siano migliorati popup o classificazione.
Il conteggio di frammenti di 1–2 parole è un indicatore diagnostico, **non** una metrica di correttezza.

| Caso | X0: fr. / brevi / errori | X1: fr. / brevi / errori |
|---|---:|---:|
| RIUNIONE-00 | 10 / 10 / no | 2 / 0 / no |
| RIUNIONE-01 | 12 / 12 / sì | 2 / 0 / no |
| RIUNIONE-02 | 12 / 12 / sì | 1 / 0 / no |
| RIUNIONE-03 | 2 / 0 / no | 2 / 0 / no |
| RIUNIONE-04 | 5 / 3 / no | 2 / 0 / no |
| RIUNIONE-05 | 3 / 0 / no | 2 / 0 / no |
| UC01-MAIN-019 | 10 / 10 / sì | 2 / 0 / no |
| UC01-MAIN-022 | 12 / 12 / no | 1 / 0 / no |
| UC01-MAIN-052 | 9 / 9 / no | 1 / 0 / no |
| UC01-MAIN-060 | 2 / 0 / no | 2 / 0 / no |

## Come decidere

1. Aprire `lfm_classificazione.csv`: controllare evento, task, completamento, negazione, testo citato e incertezza. Non basta ottenere più TASK.
2. Aprire `qwen_estrazione.csv`: controllare se X1 produce unità autonome complete, senza perdere eventi o attività.
3. Se C1 fallisce ancora i casi di negazione/completamento, non integrare LFM nella demo.
4. Se X1 è migliore, serve un secondo confronto end-to-end mantenendo C/Z/S congelati prima di adottarla.
5. Nessun risultato in questo file dimostra generalizzazione: tutti questi casi sono già noti durante lo sviluppo.

**Errori infrastrutturali/JSON riportati:** nessuno rilevato nei riepiloghi; verificare comunque i dettagli.

Il prototipo web originale e i pesi dei modelli non sono modificati. Nessun task/evento viene scritto.
