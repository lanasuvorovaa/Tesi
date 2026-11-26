# Prossimo passo: I1-R senza cambiare il classificatore

**Obiettivo:** verificare se una migliore qualità semantica dell'input strutturato corregge errori di C2-CTX a **parità di prompt, modello, parametri e azioni X2 validate**.

**Fase 1 — gold di ingresso:** revisionare con regole esplicite un sottoinsieme mirato di note (`008`, `017`, `019`, `020`, `021`, `025`, `026`, `028`, `030`, `034`, `038`, `039`), prima di osservare le nuove predizioni. Indicare ruoli, scope, evidenza testuale, e ciò che rimane non risolto. Non promuovere a "gold indipendente" una correzione preparata dagli autori del sistema su note già conosciute.

**Fase 2 — adattatore I1-R:** mantenere gli stessi action ID e le medesime citazioni valide; migliorare soltanto la rappresentazione contestuale, usando `modality`, `polarity`, `speaker`, `completion`, `discourse`, `time`, `place`, `recipient` dove esistono evidenze, con stato `unresolved` per informazioni non stabilite. Non recuperare automaticamente le azioni scartate a monte.

**Fase 3 — prova appaiata:** inviare a C2-CTX v01 identico gli input I1 e I1-R, salvando entrambi gli output. Valutare tipo di evento/task, intento, soggetto, negazione, stato e nuove confusioni; registrare chiamate, latenza e differenze. Se cambia lo schema di input o il prompt, etichettare l'esperimento come modifica combinata (non puro effetto dati).

**Fase 4 — decisione:** solo se le revisioni dell'input aiutano senza regressioni critiche, procedere alla progettazione del classificatore v02. La configurazione stabile non cambia.
