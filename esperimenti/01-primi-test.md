# 01 — Prime prove sulle note e definizione dei casi

## Da dove nasce l'idea

All'inizio volevo capire una cosa semplice: un modello linguistico piccolo, che gira in locale sul Mac, riesce a leggere una nota scritta in modo libero e a riconoscere che cosa contiene? Cioè se c'è un'attività da fare, un appuntamento, una data, una negazione, oppure solo un'informazione che non deve diventare un promemoria.

Provando le prime note mi sono accorta che non bastava trovare un verbo come «devo». Il sistema doveva distinguere una cosa da fare da un desiderio («mi piacerebbe imparare il portoghese»), da un'azione già fatta («ho già pagato la bolletta»), da una frase citata («ho salvato questa strofa inventata: …») o da qualcosa che non va fatto («non prenotare nessuna stanza»). Da qui è nata l'esigenza di avere un insieme fisso di casi su cui confrontare le varianti, invece di provare ogni volta note diverse.

## Cosa ho fatto

Ho usato la pipeline della demo UC-01 v0.3, che in questa fase era la configurazione di riferimento: X0 (estrazione dei frammenti) → C0 (classificazione di tipo e intenzione) → Z (controlli di ammissibilità) → S (selettore, al massimo un popup per nota).

- Modello: Qwen3-1.7B quantizzato Q4 (GGUF), con llama.cpp in locale, solo CPU, su un MacBook Pro Intel (i7 sei core 2,6 GHz, 16 GB RAM).
- Parametri: temperatura 0, seed 42, massimo 350 token, contesto 4096, output in JSON vincolato da schema.
- Tipi: `TASK`, `EVENT`, `FACT`. Intenzioni: `COMMITTED`, `TENTATIVE`, `COMPLETED`, `INFORMATIONAL` (in seguito anche `NEGATED` e `HYPOTHETICAL`).

I casi sono di due tipi:

1. **Sei parafrasi della stessa nota** (`RIUNIONE-00` … `RIUNIONE-05`): una riunione con Chiara martedì alle 9 e delle slide da preparare prima, scritte in sei modi diversi. Servivano a vedere se lo stesso contenuto, detto in altro modo, produce lo stesso risultato.
2. **Development set di 24 note** (`UC01-MAIN-…`), congelato e usato da qui in avanti in quasi tutte le prove. Contiene task espliciti, eventi fissati, azioni già concluse, negazioni, ipotesi, desideri, testo citato, una data vaga e un comando fuori dominio (la playlist).

Le note sono sintetiche, scritte da me per coprire questi casi. Nelle fasi successive ho aggiunto altri set diagnostici e un insieme di 40 note nuove, che sono descritti negli esperimenti dove li ho usati.

## Cosa si vede

**Parafrasi della riunione.** Le sei note dicono la stessa cosa, ma il risultato cambia con la formulazione:

| Caso | Frammenti | Popup proposto | Come viene etichettata la preparazione delle slide |
|---|---:|---|---|
| RIUNIONE-00 | 3 | EVENT «La riunione con Chiara» | FACT/COMPLETED |
| RIUNIONE-01 | 2 | EVENT «Martedì alle 9 ho una riunione con Chiara» | FACT/COMMITTED |
| RIUNIONE-02 | 3 | TASK «Devo finire le slide» | TASK/COMMITTED |
| RIUNIONE-03 | 2 | EVENT «Per martedì alle 9 è fissata la riunione con Chiara» | FACT/TENTATIVE |
| RIUNIONE-04 | 3 | EVENT «vedrò Chiara in riunione» | FACT/COMMITTED |
| RIUNIONE-05 | 1 | EVENT (tutta la nota in un solo frammento) | non separata |

La riunione viene quasi sempre riconosciuta, ma il compito delle slide diventa TASK solo in un caso su sei. In RIUNIONE-00 e RIUNIONE-04 il popup è un pezzo di frase senza l'orario, perché X0 ha messo data e riunione in frammenti diversi.

**Development set (24 note, 45 frammenti).** La pipeline di riferimento ha prodotto 11 popup (10 `PROPOSE`, 1 `CLARIFY`), nessuna segnalazione tecnica, tempo medio di inferenza 3,54 s per nota. Guardando le note una per una:

- funziona sui casi più netti: «Domani devo prenotare il furgone» (019) viene proposto e «Ieri ho restituito le chiavi» no. Gli appuntamenti fissati di 080 e 107 diventano EVENT,
- in 060 («Non devo più chiamare il fornitore, devo invece scrivergli una mail») la mail viene etichettata FACT e non c'è nessun popup: l'attività reale si perde,
- in 062 il popup è «La riunione con Chiara», senza giorno e ora, e le slide sono etichettate FACT/COMPLETED,
- in 024 («imballare i libri, avvisare il condominio e ritirare gli scatoloni») viene proposta una sola delle tre attività, e le altre due sono etichettate FACT/TENTATIVE ed EVENT,
- in 022 e 095 i comandi citati vengono in parte classificati come impegni («Domani cancello ogni appuntamento», «cancella il calendario» come EVENT/COMMITTED), ma Z li blocca e non compare nessun popup,
- in 052 («il prossimo fine settimana») viene proposto un evento anche se la data non permette di fissarlo: qui servirebbe una domanda di chiarimento.

## Cosa ne concludo

Da queste prove ho capito che il numero di popup non dice se il sistema funziona. Un popup può essere giusto, incompleto (la riunione senza ora), oppure sbagliato. E l'assenza di popup può essere corretta (la strofa citata) o una perdita (la mail di 060). Per questo dalle prove successive ho valutato separatamente correttezza, completezza e attribuzione della proposta.

Ho anche visto che un errore finale può nascere in punti diversi: X0 che spezza la frase, C che sbaglia l'etichetta, Z che blocca o lascia passare, S che sceglie un solo frammento. Per capirne la causa serve cambiare un componente alla volta, ed è così che ho impostato i confronti successivi (modelli, classificatore, selettore, estrazione).

Ho mantenuto X0+C0+Z+S con Qwen3-1.7B come riferimento. Limiti: le note sono sintetiche e poche, le ho scritte io e le ho usate più volte per prendere decisioni, quindi il development set non è un test indipendente. In questa fase non c'era ancora una revisione manuale con etichette attese: le osservazioni sopra sono una lettura qualitativa degli output. I tempi riguardano questo Mac Intel e non un telefono.

## Dati

`01-primi-test-dati.csv` (30 righe): una riga per nota con l'esito della pipeline di riferimento X0+C0+Z+S su Qwen3-1.7B. `prova` distingue le sei parafrasi (`parafrasi_riunione`, dalla prova a 10 note) dalle 24 note di sviluppo (`development24`). `data_riferimento` è la data usata per interpretare «domani», «martedì» ecc. `etichette` elenca i frammenti di X0 come `TIPO/INTENZIONE:testo`, separati da ` | `. `z_ammessi` e `selettore_ammessi` sono i candidati rimasti dopo Z e quelli ammessi dal selettore. `decisione` è `PROPOSE`, `CLARIFY` (popup con richiesta di chiarimento) o `NO_POPUP`. `tempo_s` è il tempo di inferenza per nota.
