# Protocollo sperimentale X2 — UC-01

**Baseline candidata invariata:** `X0+C2+Z+S2-V`. Le 40 note già note non sono un nuovo holdout.

**Varianti:** X0, X1, X2, stesso modello Qwen3-1.7B Q4, parametri deterministici e stessa data di riferimento. C2, Z e S2-V verificati mediante hash del pacchetto congelato. X2 usa un formato JSON strutturato con `actions`, span e context; la proiezione letterale separata è parte del trattamento X2.

**Ipotesi:** X2 può preservare atomicità e riferimenti contestuali in metadati dedicati. Questo non implica che migliori automaticamente la qualità finale del popup, poiché il downstream riceve solo `action_quote`.

**Metriche:** (1) 40/40 elaborazioni senza errori; (2) azioni raw e validate; (3) invalidità degli span di azione e contesto, e quota rifiuti; (4) azioni mancanti, fuse o spezzate; (5) presenza di vincoli essenziali nei context; (6) accuratezza per nota A/P/E/U dei popup, anche assenza di popup; (7) falsi popup, opportunità perse, regressioni appaiate rispetto a X0; (8) latenza, chiamate al modello. I conteggi automatici non sostituiscono la revisione umana.

**Rischi predefiniti:** omissione di azioni per offset errati; perdite di qualificatori `non`, `forse`, `già` nella proiezione a C2/Z; frammenti privi di soggetto o verbo; relazioni/anafore non risolte; schema più complesso per un modello compatto.

**Criterio decisionale:** non promuovere X2 sulla base di questo set di sviluppo. Dopo la diagnosi, bloccare schema/prompt/proiezione e provare su note nuove con gold indipendente, registrato prima dell'inferenza. Se X2 necessita di un adattatore semantico che porti il contesto a C2 o a Z, progettare esplicitamente un secondo esperimento con interfaccia modificata; non presentarlo come configurazione con C2/Z identici.
