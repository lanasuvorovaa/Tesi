# Roadmap concreta dalla prova C0/C1

## Immediatamente: revisione del confronto (development)
1. Aprire `04_Dati_CSV/05_C0_C1_confronto_frammenti.csv` e `06_C0_C1_confronto_note.csv`. Le colonne di revisione sono ancora da compilare: non dedurne un gold già esistente.
2. Etichettare **manualmente**, per ogni frammento, tipo e intenzione attesi, correttezza C0 e C1, motivazione della scelta, eventualmente con una categoria «ambiguo / contesto insufficiente». Separare giudizio sul frammento e giudizio sulla nota/popup.
3. Esaminare tutti i casi in cui C0 e C1 divergono, non solo quelli dove C1 sembra migliorare. Controllare soprattutto TASK/EVENT, `COMMITTED`, `TENTATIVE`, `COMPLETED`, `NEGATED`, `HYPOTHETICAL`, `INFORMATIONAL`, citazioni, data vaga e contenuto condizionale.
4. Valutare popup proposti e mancati: falso positivo, falso negativo, correttezza del contenuto, necessità di chiarimenti, rischi di azione indebita. Tracciare anche errori attribuibili a X0, a C, a Z o a S, senza attribuirli automaticamente al classificatore.
5. Calcolare soltanto **dopo il gold** i confronti quantitativi pertinenti (per es. accuratezza per tipo/intenzione, errori critici e qualità del popup). Documentare campione ridotto e dati già visti in development.

## Decisione C1
6. Se C1 genera regressioni di sicurezza non accettabili, mantenere C0. Se emergono regolarità utili, formulare una **C2 mirata** in una nuova prova controllata, modificando un unico componente per volta e non riusando indiscriminatamente il campione come validation.
7. Non correggere X, C, Z e S contemporaneamente: test di ablazione e confronto causale ne risulterebbero compromessi.

## Dopo la decisione
8. Definire e congelare una vera partizione di validation/test indipendente; non promuovere le 24 note conosciute a test finale.
9. Solo se necessario, discutere nuove modifiche a X o alla progettazione dati basandosi su errori attribuiti correttamente. Non rifare il database o cambiare modello per semplice impressione.
10. Riportare risultati misurati, limitazioni dell'hardware on-device e procedure riproducibili nella tesi; verificare separatamente UC-02 e i benchmark A/B/C/D previsti.
