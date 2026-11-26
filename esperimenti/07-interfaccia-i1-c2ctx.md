# 07 — Interfaccia contestuale I1 e classificatore C2-CTX v01

## Da dove nasce l'idea

Il confronto tra P0 e P1 mi aveva lasciato con un problema aperto. P0 passava al classificatore solo l'azione atomica e perdeva dettagli come scadenze e negazioni (16 corretti, 12 parziali, 12 errati sulle 40 note). P1 passava una clausola più lunga e dava proposte più complete (25 corretti, 4 parziali, 11 errati), ma a volte includeva più attività insieme o introduceva falsi popup, per esempio sui desideri delle note 019 e 024.

Mi sono chiesta se si potesse tenere separata l'azione dal suo contesto, invece di allungare sempre la citazione. Ho quindi progettato un'interfaccia, che ho chiamato I1, in cui ogni azione ha:

- una citazione contigua della nota (`action_evidence`), con gli indici calcolati in Python e non chiesti al modello;
- una lista di riferimenti al contesto (`context_refs`), ognuno con citazione esatta, ruolo (`time`, `place`, `recipient`, `condition`, ...) e portata, cioè a quali azioni si applica.

Siccome il classificatore C2 accetta una sola stringa, passargli azione e contesto separati significa cambiare il significato del suo input. Per questo ho scritto un prompt nuovo, C2-CTX, che oltre a `kind` e `intent` restituisce anche `subject_owner` (chi deve fare l'azione), `polarity`, `completion` e `uncertain`.

## Cosa ho fatto

- **Dati:** le stesse 40 note sintetiche dei test precedenti. Ho usato le azioni già estratte e validate da X2 v02 e le ho congelate: sono 39 azioni, presenti in 31 note. Le altre 9 note non hanno azioni validate da X2.
- **Interfaccia:** I1 viene ricostruita automaticamente dalle estrazioni X2. Il controllo verifica che ogni citazione corrisponda esattamente al testo e che la portata sia coerente, ma non dice se il ruolo assegnato abbia senso.
- **Confronto:** per ogni azione ho chiamato sia C2 (prompt congelato) sia C2-CTX, quindi 78 classificazioni. Modello Qwen3-1.7B Q4 in locale con llama.cpp, `temperature=0`, `seed=42`, `max_tokens=350`, contesto 4096, solo CPU.
- **Cosa non ho fatto:** Z e S2-V non sono stati eseguiti, perché l'output di C2-CTX non è compatibile con loro senza un adattatore. Il test riguarda solo la classificazione e non dice nulla sui popup finali. Il gold non è stato letto dal runner.

Dopo l'esecuzione ho rivisto a mano le azioni in cui C2 e C2-CTX davano etichette diverse.

## Cosa si vede

Tutte le 78 risposte sono JSON validi rispetto allo schema (39 per C2 e 39 per C2-CTX). La validità formale però non dice nulla sulla correttezza.

| | C2 | C2-CTX |
|---|---:|---:|
| TASK | 24 | 38 |
| EVENT | 6 | 1 |
| FACT | 9 | 0 |

C2-CTX tende a trasformare quasi tutto in TASK. I due classificatori differiscono su `kind` o `intent` in **16 azioni su 39**; nelle altre 23 queste due etichette restano uguali. Nella revisione preliminare dei 16 cambiamenti:

| Giudizio sul cambiamento | Azioni |
|---|---:|
| Miglioramento plausibile | 4 |
| Peggioramento | 10 |
| Non determinabile | 2 |

Questi giudizi riguardano solo le azioni che cambiano, non l'accuratezza complessiva del classificatore.

Alcuni casi concreti:

- **Miglioramenti:** «Stasera ricordarmi di rinnovare la tessera della biblioteca» (002) passa da FACT/INFORMATIONAL a TASK/COMMITTED, che è corretto. Lo stesso succede per «stampare l'etichetta» (030) e «controllo il numero di serie» (032). Nella 024 la maratona passa da COMMITTED a TENTATIVE, più vicino al senso della nota.
- **Eventi diventati task:** «La visita con l'oculista è confermata per venerdì alle 15:30» (008), il colloquio online (009), la prova dell'orchestra (011) e l'incontro del gruppo di lettura (034) erano EVENT con C2 e diventano TASK/COMMITTED.
- **Azioni di altri o non azioni:** in «Non devo più ritirare il pacco: ci pensa già Alessia» (025) si passa da TASK/NEGATED a TASK/COMMITTED. «Mi piacerebbe aprire un laboratorio di ceramica, prima o poi» (020) diventa TASK/COMMITTED. Le frasi citate di 038 (un romanzo) e 039 (una frase di prova) diventano task da fare.

Anche gli attributi nuovi sono poco credibili:

- `subject_owner=SELF` in **39/39** azioni, anche dove l'azione è di un'altra persona (per esempio la segreteria che aspetta il corriere, nota 013);
- `polarity=POSITIVE` in 37/39 (le altre 2 UNCLEAR), quindi nessuna negazione riconosciuta;
- `completion=DONE` in 11/39, anche per azioni future come «devo scaricare il QR code» (028);
- `uncertain=True` in 28/39.

Infine, una parte degli errori nasce prima del classificatore. Alcune azioni estratte da X2 non sono autonome («prenotata» in 012, «per venerdì alle 15:30» come seconda azione in 008), e alcuni ruoli del contesto sono discutibili, come l'intera frase della visita etichettata `time` nella 008. In più, I1 ha segnalato 17 problemi di conversione: 16 ruoli `object_reference` non supportati e una relazione tra azioni (nota 026) non trasferita.

## Cosa ne concludo

Non adotto C2-CTX v01 e non lo collego a Z e S2-V. Recupera alcuni task espliciti, ma sbaglia in modo grave proprio sui punti che volevo migliorare: eventi, soggetto, negazioni e testo citato. La configurazione candidata resta `X0 → C2 → Z → S2-V`.

Rimane però una domanda: quanto di questi errori dipende dal classificatore e quanto dai contesti che gli passo, che già a una prima occhiata non sembravano sempre corretti? Prima di riscrivere il prompt ho deciso di controllare i dati in ingresso (esperimento 08).

Limiti: le 40 note sono sintetiche e già usate negli esperimenti precedenti, quindi non sono un test indipendente. La revisione dei cambiamenti è preliminare e tutte le righe sono ancora segnate come da confermare. Il test misura la classificazione, non i popup.

## Dati

`07-interfaccia-i1-c2ctx-dati.csv` (39 righe, una per azione) è la tabella di revisione del confronto. `caso` e `azione_id` identificano l'azione; `nota` e `azione` riportano il testo della nota e la citazione dell'azione; `contesti` è la lista dei riferimenti I1 in JSON; `C2_kind`/`C2_intent` e le colonne `C2_CTX_*` sono le etichette dei due classificatori; `etichette_differenti` vale 1 se cambia `kind` o `intent`; `giudizio_modifica` (INVARIATO, MIGLIORA, PEGGIORA, INCERTO) e `motivazione` sono il giudizio della revisione preliminare; `verifica_umana` indica che il giudizio è ancora da confermare.
