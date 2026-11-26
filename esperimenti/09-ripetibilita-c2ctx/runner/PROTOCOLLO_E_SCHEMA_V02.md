# Protocollo di ripetibilità e ipotesi per C2-CTX v02

## Fase A — Ripetibilità prima di intervenire

**Ipotesi:** a parità di input, modello, prompt, schema e parametri, il classificatore può restituire classificazioni diverse. La verifica non riguarda la bontà del gold, ma la variabilità osservata.

- 20 azioni di cui 18 con contesti modificati e 2 controlli invariati; 3 ripetizioni per azione.
- Si esegue con `temperature=0`, `seed=42`, `max_tokens=350`, `context=4096`, `ngl=0`, `threads=6` e server isolato già previsto dal runner originale.
- Misure: 60 risposte previste; percentuale JSON validi; azioni con tutte e sei le etichette identiche in tre run; variazioni per singolo attributo; ripetizioni divergenti; tempi solo come metrica secondaria.
- Ordine diretto/inverso/diretto, non per attribuire differenze a un'unica causa, ma per non associare completamente round e posizione di esecuzione.
- Interpretazione: l'instabilità si documenta; non è possibile inferire che la stessa risposta sia semanticamente giusta o che la variabilità sia causata da un solo fattore tecnico.

## Fase B — Bozza progettuale (non implementata): C2-CTX v02

In base agli errori documentati, un prossimo classificatore più parsimonioso dovrebbe distinguere le seguenti decisioni, senza moltiplicare campi non necessari:

1. **Natura dell'elemento:** `TASK | EVENT | FACT` (gli appuntamenti confermati non sono TASK).
2. **Titolarità/voce:** `SELF | THIRD_PARTY | QUOTED | UNCLEAR` (una citazione non diventa un impegno personale).
3. **Stato di azionabilità:** `ACTIONABLE | TENTATIVE | NEGATED | DONE | INFORMATIONAL | UNCLEAR`.

I campi dovranno essere vincolati da evidenze testuali e controlli espliciti; il modello non deve inferire soggetto, negazione o completamento assenti. Prima di sviluppare il prompt occorre decidere l'ordine delle decisioni e verificare se il modello è in grado di rispettare lo schema con affidabilità. Le relazioni X2 non proiettate, gli errori di estrazione e le azioni mancanti rimangono fuori portata.

**Non si asserisce che questi valori migliorino già i risultati**. Lo schema è una proposta di studio, non un classificatore validato. Per l'eventuale confronto v01/v02, congelare schema, testset nuovo e criteri gold prima dell'inferenza. Non modificare la configurazione candidata `X0+C2+Z+S2-V`.
