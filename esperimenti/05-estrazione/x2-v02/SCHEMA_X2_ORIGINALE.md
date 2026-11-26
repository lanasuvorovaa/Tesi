# UC-01 — Specifica preliminare X2 (v0.1)

**Stato:** proposta progettuale; nessuna modifica alla pipeline, nessun nuovo risultato empirico.
**Obiettivo:** separare le unità operative atomiche dai dettagli contestuali, senza inferire fatti assenti e mantenendo le citazioni verificabili contro la nota originale.

## Contratto dati

Per ogni nota, X2 produce `actions[]`. Ogni voce contiene:
- `id`: identificatore locale progressivo;
- `action_quote`: testo **letterale, contiguo** ricopiato dalla nota e riferito a una sola azione; non necessariamente autosufficiente se un dato è esterno alla citazione;
- `action_span`: intervallo `[start,end)` nell'originale (offset di caratteri Unicode Python, inclusivo all'inizio, esclusivo alla fine), tale che `nota[start:end] == action_quote`;
- `context[]`: riferimenti contestuali **letterali** e verificabili con `quote`, `span` e `role`; ruoli ammessi `time`, `place`, `recipient`, `object_reference`, `condition`, `polarity`, `modality`, `other`;
- `relations[]`: legami espliciti con altre azioni, per esempio `before`, `after`, `depends_on`, `contrasts_with`, solo se attestati nel testo.

`action_quote` è una **evidenza**, non il testo del popup. Il popup può richiedere la presentazione separata di `action_quote` e `context`, senza inventare una nuova citazione. Qualsiasi ricomposizione del testo è un componente distinto e va validata.

## Vincoli

1. **Atomicità:** una voce per azione; non fondere `pagare il bollo` e `inviare la ricevuta`.
2. **Fedeltà:** ogni stringa presentata come citazione deve essere una sottostringa contigua della nota; non riorganizzare parole.
3. **Ambiguità:** conservare negazioni e incertezza in `context` anche se esterne alla porzione verbale; non interpretare `forse` come impegno.
4. **Anafora:** riferimenti come `Quello firmato` restano letterali; un eventuale antecedente `modulo` va rappresentato con un riferimento puntuale e non aggiunto come se fosse testo originale della citazione.
5. **Molteplicità:** `actions[]` può contenere più voci, ma la politica corrente di **massimo un popup per nota** resta invariata.
6. **Nessuna decisione anticipata:** X2 estrae anche azioni negate o già completate se rilevanti alla comprensione; C2, Z e S2-V continuano a giudicare l'eleggibilità. Il contesto negativo deve raggiungerli per evitare errori.
7. **Rifiuto sicuro:** se gli intervalli non corrispondono al testo, l'elemento viene scartato e registrato; non si corregge silenziosamente il testo.

## Compatibilità con la pipeline congelata

L'output di X2 **non è direttamente compatibile** con l'attuale input a citazioni semplici di C2. Serve definire una *proiezione X2→quote* inclusa e versionata all'interno dell'esperimento X2; C2, Z, S2-V rimangono byte-per-byte invariati.

La proiezione **non deve spacciarsi per una citazione originale** quando accosta parti non contigue. Per un primo test end-to-end rigoroso è consentita esclusivamente la `action_quote` letterale, con i metadati contestuali valutati separatamente. Se così si perdono qualificatori fondamentali per C2/Z, va registrato come limite e serve un protocollo successivo per un'interfaccia a contesto, non una modifica implicita dei componenti congelati.

## Esempi di comportamento atteso

- **031** — `Domani devo pagare il bollo e inviare la ricevuta alla contabilità.` → due azioni: `devo pagare il bollo` e `inviare la ricevuta alla contabilità`; contesto temporale `Domani` associato a entrambe. Questo è un *obiettivo*, non un risultato osservato.
- **033** — `Per il mercatino sabato preparo i cartellini, porto il resto e avviso Martina.` → tre azioni, contesto condiviso `Per il mercatino sabato`, senza fonderle.
- **035** — `Con Elena, non con Paolo, mercoledì devo rivedere le slide.` → azione `devo rivedere le slide`, contesto `Con Elena`, `non con Paolo`, `mercoledì`; vietato produrre una falsa citazione riorganizzata.
- **036** — `Il modulo per l’iscrizione l’ho scaricato. Quello firmato devo consegnarlo venerdì.` → distinguere attività già completata e consegna futura; non risolvere anafora inventando una nuova quote.
- **028** — `Non devo stampare i biglietti, ma domani devo scaricare il QR code.` → due azioni distinte; negazione solo sulla prima, `domani` sulla seconda.

## Criteri di valutazione

Per ciascuna nota misurare separatamente: numero di azioni riconosciute, precisione dei confini, copertura di dettagli contestuali espliciti, fedeltà degli span, azioni fuse o spezzate, e qualità end-to-end A/P/E secondo il protocollo già usato. Valutare in particolare i casi 001, 005, 006, 028, 030–033, 035–037, senza considerarli holdout indipendente.
