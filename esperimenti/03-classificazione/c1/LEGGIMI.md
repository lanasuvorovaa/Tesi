# Classificazione C1 — prova sperimentale UC-01

Questo pacchetto confronta **Qwen3-1.7B con il classificatore attuale C0** e **lo stesso Qwen3-1.7B con un prompt C1 sperimentale**.

Non sostituisce la demo del professore. Non modifica il modello GGUF, il dataset, né il codice originale della pipeline. L'esperimento è **solo development**: i 24 casi sono già stati utilizzati per prendere decisioni durante la ricerca, quindi non costituiscono validation indipendente.

## Che cosa cambia

La sola modifica è `prompt_C1.txt`: definizioni e contrasti che cercano di distinguere meglio:

- le azioni da svolgere anche in forma impersonale (es. «Il documento va consegnato»);
- gli appuntamenti effettivamente fissati, distinti dalle attività;
- le azioni già concluse, negate, ipotetiche o soltanto desiderate;
- le informazioni e le citazioni che non rappresentano impegni personali.

I due classificatori ricevono **gli stessi frammenti**, estratti una sola volta con **X0** dalla nota. Restano invariati `EXTRACT_X`, il formato JSON vincolato, le regole Z, il selettore S, il modello, i parametri di decoding e le 24 note di development. Il codice congelato è copiato dalla demo precedente senza modifiche.

## Avvio sul Mac

1. Estrai lo ZIP sul Desktop mantenendo il nome `classificazione_c1_qwen3_uc01_v01`.
2. Lascia sul Desktop la cartella `confronto_slm_uc01_v01` che abbiamo usato per i confronti fra modelli: contiene il runtime di `llama.cpp` aggiornato **e l’ambiente Python con `jsonschema`**.
3. Il modello `~/models/qwen3-1.7b-q4.gguf` deve essere già presente.
4. Apri **un solo Terminale** e avvia:

```bash
cd "$HOME/Desktop/classificazione_c1_qwen3_uc01_v01"
bash esegui.command
```

Il comando esegue prima i test locali, poi avvia Qwen3-1.7B in automatico sulla porta `8091`, analizza le 24 note e chiude soltanto il server avviato dallo script. **Non occorre avviare la demo né un altro server.** La porta `8091` deve essere libera. Il programma non interferisce con la demo sulla porta `8080`.

Non è richiesto alcun nuovo download o fine-tuning. Se manca la cartella del runtime o il modello, il programma mostra l'errore e si ferma senza modificare file esistenti.

## File prodotti

Nella sottocartella `risultati/c0_vs_c1_YYYYMMDD_HHMMSS` troverai:

- **`report.md`**: confronto nota per nota, conteggi operativi e tempi di inferenza;
- **`confronto_frammenti.csv`**: per ogni *stesso* frammento, etichette C0/C1 e decisioni dei controlli e del selettore;
- **`confronto_note.csv`**: per ogni nota, etichette, popup e tempi a confronto;
- `revisione_frammenti.csv` e `revisione_note.csv`: gli stessi risultati, con colonne vuote per la revisione semantica;
- `dettagli/*.json`: risposte effettive del modello nelle due condizioni e tracce, utili in caso di incongruenze;
- `manifest.json`: hash dei prompt, dei componenti e dei pesi per la riproducibilità;
- `llama_server.log`: messaggi del server locale.

**Per proseguire**, carica `report.md`, `confronto_frammenti.csv` e `confronto_note.csv`. Se qualche dettaglio non è chiaro, possiamo consultare i JSON già salvati.

## Come decidere se C1 è migliore

I soli conteggi di popup o di etichette cambiate **non sono metriche di qualità**. Bisogna controllare semanticamente i candidati e la decisione finale.

Diamo particolare attenzione a questi casi del development:

- `UC01-MAIN-062`: riunione con Chiara e slide ancora da preparare;
- `UC01-MAIN-019`: attività già compiuta e nuova attività;
- `UC01-MAIN-060`: telefonata negata e mail da scrivere;
- `UC01-MAIN-080` e `UC01-MAIN-107`: appuntamenti fissati;
- `UC01-MAIN-022`: testo riportato come citazione, non istruzione;
- `UC01-MAIN-052`: visita indicata con data vaga, per cui serve un chiarimento prima di una proposta operativa;
- `UC01-MAIN-028` e `UC01-MAIN-088`: ipotesi e desiderio generico;
- `UC01-MAIN-093` e `UC01-MAIN-094`: completamento e negazione.

Un miglioramento delle attività non deve produrre nuove proposte su contenuti negati, conclusi o meramente citati. Una risposta JSON formalmente valida può comunque essere semanticamente scorretta. Se X0 perde un elemento, C1 non può recuperarlo: l'errore va attribuito all'estrazione.

Il test non effettua scritture su appunti, attività o calendario, non contatta servizi cloud e non include dati gold nelle chiamate al modello. Sono creati solo report nella cartella locale del pacchetto. Non abbiamo verificato qui la qualità effettiva di C1: è necessario eseguire il modello sul Mac.
