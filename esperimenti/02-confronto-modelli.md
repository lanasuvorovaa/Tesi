# 02 — Confronto tra modelli: Qwen3-1.7B, Qwen3.5-2B, LFM2.5-1.2B

## Da dove nasce l'idea

Con Qwen3-1.7B la pipeline funzionava sui casi semplici ma sbagliava ancora parecchie etichette (esperimento 01). Prima di continuare a modificare prompt e regole volevo capire se convenisse cambiare modello. Ho quindi cercato alternative di dimensione simile, che potessero girare in locale e in prospettiva su un telefono, e ho scelto Qwen3.5-2B e LFM2.5-1.2B-Instruct. In una fase ancora precedente avevo considerato anche Qwen3-0.6B ed EuroLLM-1.7B, ma di quelle prove non ho risultati sufficienti per un confronto.

## Cosa ho fatto

Tutti i modelli in formato GGUF Q4 (Qwen3-1.7B Q4 già presente sul Mac; Qwen3.5-2B Q4_K_M da bartowski; LFM2.5-1.2B-Instruct Q4_K_M ufficiale Liquid AI), una versione aggiornata e separata di llama.cpp, un modello alla volta sulla porta locale 8091, solo CPU. Parametri uguali per tutti: temperatura 0, seed 42, massimo 350 token, contesto 4096, JSON vincolato da schema. Nessuna ottimizzazione dei prompt per famiglia di modello.

Le prove sono state quattro, in sequenza:

1. **Fase 1, 10 note:** le sei parafrasi della riunione e quattro casi del development set (019 attività conclusa più nuova attività, 022 testo citato, 052 data vaga, 060 negazione). Tre modelli, stessa pipeline X0+C0+Z+S.
2. **Diagnostico su LFM2.5:** stessi frammenti X0, classificati con C0 e con un prompt C1 sperimentale, per vedere se il problema fosse il prompt.
3. **Diagnostico su Qwen3.5:** solo estrazione, X0 contro un prompt X1 che chiede segmenti completi e vieta parole isolate.
4. **Fase 2, 24 note di sviluppo:** Qwen3-1.7B con X0+C0+Z+S contro Qwen3.5-2B con X1+C0+Z+S. Qui cambiano insieme modello e prompt di estrazione, quindi il confronto è tra sistemi e non tra modelli.

## Cosa si vede

**Fase 1 (10 note).**

| Modello | Segnalazioni | Popup | Tempo medio (s) |
|---|---:|---:|---:|
| Qwen3-1.7B | 0 | 8 | 5,54 |
| Qwen3.5-2B | 3 | 6 | 17,11 |
| LFM2.5-1.2B | 1 | 9 | 9,6 |

Il numero di popup qui inganna. Qwen3.5-2B con il prompt X0 spezzava le note in singole parole: in sei note su dieci tutti i frammenti erano di una o due parole (per esempio 12 frammenti per RIUNIONE-01), e tra i popup proposti c'erano «devo», «Devo», «Prima devo», «Ricordarmi». Le tre segnalazioni sono citazioni non valide o non univoche. LFM2.5-1.2B proponeva un popup in 9 note su 10, ma sempre come TASK, anche per «Per martedì alle 9 è fissata la riunione con Chiara». In 060 è stato l'unico a proporre «devo invece scrivergli una mail», ma il diagnostico sotto mostra che classificava come TASK/COMMITTED anche la chiamata negata.

**Diagnostico LFM2.5 (18 frammenti).** Con C0 tutti i 18 frammenti erano TASK/COMMITTED. Con C1 quattro frasi sulla riunione diventano EVENT, ma restano TASK/COMMITTED anche «Ieri ho restituito le chiavi» (già fatto), «Non devo più chiamare il fornitore» (negato) e «Domani cancello ogni appuntamento» (testo citato). La confusione tra evento e attività, e l'assenza di distinzione per negazioni e azioni concluse, non si risolvevano cambiando prompt.

**Diagnostico Qwen3.5 (estrazione).** Con X1 i frammenti diventano uno o due per nota, nessuno di una o due parole e nessuna segnalazione. In alcuni casi però X1 unisce tutta la nota in un solo segmento (RIUNIONE-02) o tiene solo una parte (in 022 estrae solo «Ho salvato questa strofa inventata»).

**Fase 2 (24 note di sviluppo).**

| Sistema | Segnalazioni | Popup | Tempo medio inferenza (s) |
|---|---:|---:|---:|
| Qwen3-1.7B, X0+C0+Z+S | 0 | 11 | 3,54 |
| Qwen3.5-2B, X1+C0+Z+S | 3 | 7 | 4,49 |

Qwen3.5-2B segmenta meglio, ma classifica come `INFORMATIONAL` gran parte dei frammenti (17 su 33 sono FACT/INFORMATIONAL). Di conseguenza perde appuntamenti chiari: «La visita dal dentista è confermata per il 20 ottobre» (080) diventa FACT/INFORMATIONAL e «Giovedì alle 16 ho la visita con la fisioterapista» (107) EVENT/INFORMATIONAL, entrambi senza popup; in 024 tutte e tre le attività del trasloco sono INFORMATIONAL. Propone invece un popup di chiarimento su «Potrei incontrare Andrea o Luca venerdì» (076), che è solo un'ipotesi. I task con «devo» espliciti (011, 019, 079, 097, 118) vengono proposti da entrambi i sistemi.

## Cosa ne concludo

Ho mantenuto Qwen3-1.7B come modello di riferimento per le prove successive. Qwen3.5-2B con X1 frammenta meglio alcune note, ma nel confronto end-to-end non supera il riferimento, ha più segnalazioni e perde eventi confermati. LFM2.5-1.2B confonde stabilmente TASK ed EVENT e non distingue negazioni e azioni concluse, anche con il prompt C1. Questo non significa che Qwen3-1.7B sia il modello migliore in assoluto: è rimasto la scelta di lavoro per il prototipo, e da qui ho deciso di concentrarmi sui singoli componenti (prima il classificatore, esperimento 03).

Limiti: tutte le note sono note di sviluppo già conosciute, e il prompt X1 è stato scritto dopo aver visto proprio questi esempi, quindi nessuna di queste prove è una validazione indipendente. I file GGUF vengono da distribuzioni diverse, quindi non è un confronto controllato delle sole architetture. Per queste prove non ho una revisione manuale compilata con le etichette attese: le osservazioni sulla correttezza sono una lettura qualitativa degli output. I tempi sono misurati su un Mac Intel con sola CPU e non dicono nulla sulle prestazioni su Android.

## Dati

`02-confronto-modelli-dati.csv` (78 righe): una riga per nota e per modello. `prova` è `fase1_10_note` (3 modelli × 10 note) o `fase2_24_note` (2 sistemi × 24 note); `sistema` indica la pipeline (`X0+C0+Z+S` o `X1+C0+Z+S`); `etichette` elenca i frammenti come `TIPO/INTENZIONE:testo`, separati da ` | `; `z_ammessi` e `selettore_ammessi` sono i candidati rimasti dopo Z e quelli ammessi dal selettore; `decisione` è `PROPOSE`, `CLARIFY` o `NO_POPUP`; `stato` è `ESEGUITO` o `SEGNALAZIONI`, con il dettaglio in `segnalazioni` (es. `QUOTE_8_INVALID_OR_NOT_UNIQUE`, citazione non trovata o non univoca nella nota). I due diagnostici per componente (LFM2.5 C0/C1 e Qwen3.5 X0/X1) non sono nel CSV: i loro numeri sono riportati sopra.
