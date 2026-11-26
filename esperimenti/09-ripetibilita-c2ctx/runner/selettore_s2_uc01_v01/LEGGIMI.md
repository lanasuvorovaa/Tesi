# UC-01 — Esperimento controllato S2 (22 novembre 2026)

**Obiettivo:** confrontare S1, S2-V (solo veto), S2-R (solo ranking), S2-VR (combinazione) mantenendo **X0+C2+Z invariati**. I selettori sono deterministici e non effettuano nuove chiamate al modello.

## Fase 1 — Replay diagnostico immediato (non serve avviare il modello)

Estrai lo ZIP sul Desktop e nel Terminale:

```bash
cd "$HOME/Desktop/selettore_s2_uc01_v01"
bash esegui_diagnostico.command
```

I risultati precomputati si trovano anche in `risultati/diagnostico/`: `report_diagnostico.md`, `diagnostico_note.csv`, `diagnostico_candidati.csv`.

Il replay ricalcola il selettore dai 45 candidati development e 53 candidati holdout già inferiti; il gold non è consultato. Questi dati hanno guidato l'implementazione e **non sono un test indipendente**. Il confronto mantiene lo stesso frammento, le stesse etichette C2 e il gate Z per tutti i rami.

## Fase 2 — Nuove note (solo quando predisposte e annotate prima)

Non abbiamo incluso un nuovo test set nel pacchetto, per non mescolare progettazione e verifica. Creare un JSON **mai usato per decidere le regole**; separare il file gold, compilato prima dell'inferenza, e non passarlo al runner.

Esempio schema (solo formato, NON nota di validazione):

```json
{"casi":[{"id":"NUOVO-001","nota":"Devo inviare la documentazione domani.","reference_datetime":"2026-11-22T12:00:00"}]}
```

Con runtime preesistente `confronto_slm_uc01_v01` sul Desktop e modello Qwen3-1.7B Q4 già installato:

```bash
cd "$HOME/Desktop/selettore_s2_uc01_v01"
bash esegui_nuove_note.command /percorso/nuovo_testset.json
```

Il runner verifica hash di codice, prompt, modello e runtime; X0 e C2 eseguiti una sola volta per nota, Z una sola volta, poi tutti e quattro i selettori sugli stessi candidati. Nessuna scrittura su task/calendari. Output in `risultati/nuove_note_...` con `confronto_note.csv`, `confronto_candidati.csv`, dettagli, log e manifest. Non apre né legge gold. Prima della prova successiva bisogna preregistrare gold, criteri e dataset hash.

## Interpretazione

- Veto S2-V: penalizzazione **binaria** di aspirazioni esplicitamente indefinite e frasi descrittive chiaramente senza azione del soggetto; non cambia score di S1.
- Ranking S2-R: bonus per azione linguistica esplicita e lieve malus per descrizione/aspirazione; **non blocca** nessun candidato eleggibile di S1.
- S2-VR: combinazione dei due interventi, da promuovere solo se gli effetti separati non creano regressioni.
- S1 rimane congelato e la configurazione candidata X0+C2+Z+S1 **non viene sostituita** finché non ci siano risultati nuovi.
- Non sono previsti un secondo modello o modifiche a estrattore, prompt C2, Z o soglia di un popup.

**Limiti importanti:** le espressioni regolari sono euristiche linguistiche, non verifiche semantiche generali. Il veto potrebbe eliminare un impegno reale formulato in modo insolito. S2 non ricompone frammenti separati né recupera task mancanti e non corregge le classificazioni di C2. I criteri di promozione restano quelli in `PROTOCOLLO_ORIGINALE.md`.
