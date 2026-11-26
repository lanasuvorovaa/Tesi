# Replay offline delle estrazioni X2 v01

- 40 note; 66 azioni grezze.
- 61/66 citazioni di azioni con corrispondenza letterale univoca.
- 44/66 azioni accettate dopo controlli di citazioni, contesto, duplicati e relazioni.
- 22/66 azioni rifiutate.

Il replay applica l'allineatore v02 ai vecchi output v01 rimuovendo gli span forniti dal modello. **Non è un'esecuzione di X2 v02 sul modello** e non dimostra che le proposte risultanti siano corrette. I v01 contenevano relazioni autoreferenziali, context inesatti e citazioni inventate. Dettaglio in `replay_offline/`.
