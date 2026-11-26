# Prototipo locale UC-01 — versione aggiornata

Questa versione presenta il prototipo di analisi delle note in una piccola interfaccia grafica per macOS. Una nota in italiano viene esaminata sul computer attraverso un modello Qwen3-1.7B Q4 esposto da `llama.cpp`. Il sistema può **simulare una proposta** di attività o appuntamento, ma non crea promemoria, non modifica il calendario e non salva la nota.

Nel video [`Prototipo.mp4`](Prototipo.mp4) (circa 3 minuti) mostro il prototipo in funzione.

## Quale versione della ricerca utilizza

La configurazione scelta come riferimento negli esperimenti disponibili è **X0 + C2 + Z + S2-V**:

- **X0** estrae le citazioni letterali rilevanti dalla nota.
- **C2** classifica ogni citazione come attività, evento o informazione, con il relativo stato di intenzione.
- **Z** applica i controlli previsti dalla pipeline.
- **S2-V** decide se selezionare al massimo una proposta.

Le componenti sperimentali X2, P1, I1-R e C2-CTX non sono state integrate in questa versione perché i test diagnostici non ne hanno dimostrato un miglioramento sufficientemente affidabile. Non vengono presentati come risultati validati su note indipendenti.

## Avvio sul Mac

1. Installare Python 3 e avviare `llama.cpp` con il modello Qwen3-1.7B Q4 e endpoint API locale. La porta predefinita dell'interfaccia è **8091** (modificabile nel campo Server locale).
2. Installare la dipendenza Python nel terminale della cartella:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Per la **finestra grafica**, eseguire:

   ```bash
   bash esegui_prototipo.command
   ```

   In alternativa, per un test da terminale:

   ```bash
   python3 cli.py "Domani devo prenotare il furgone."
   ```

4. Per eseguire i test offline, senza modello:

   ```bash
   python3 -m unittest discover -s pipeline -p test_demo.py -v
   python3 test_integrazione.py
   ```

Se macOS non dispone di Tkinter, usare la CLI o installare una distribuzione Python che includa Tkinter. L'avvio della GUI non installa né avvia automaticamente `llama.cpp`.

## Cosa mostra

La finestra presenta la proposta, se presente, le citazioni estratte, il tipo di attività, l'intenzione, i motivi di esclusione, le avvertenze e i dati diagnostici della singola analisi. Il JSON diagnostico è mostrato sullo schermo ma non viene salvato automaticamente su disco.

## Limiti da mantenere espliciti

- La demo opera soltanto in modalità **simulazione**, senza accesso a promemoria o calendari.
- L'estrazione può perdere azioni, dettagli temporali e relazioni tra attività. Una proposta può essere incompleta o errata.
- La configurazione è una **candidata sperimentale**, non una pipeline definitivamente validata in produzione.
- I test unitari controllano il comportamento del codice su risposte simulate, **non** misurano la qualità del modello su note nuove.
- I file in `pipeline/frozen/` provengono dal riferimento sperimentale e non sono stati modificati.

Il percorso che ha portato a questa configurazione è descritto nella cartella [`../esperimenti/`](../esperimenti/), in particolare in [`04-selettori.md`](../esperimenti/04-selettori.md).
