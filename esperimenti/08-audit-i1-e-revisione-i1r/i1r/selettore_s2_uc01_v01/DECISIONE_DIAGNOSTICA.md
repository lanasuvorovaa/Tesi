# Diagnostica prerevisione: S2 su set già noti

Il replay è stato eseguito localmente senza alcuna nuova inferenza e senza usare il gold. I conteggi di selezione **non** vanno scambiati per correttezza automatica.

| Set noto | S1 | S2-V | S2-R | S2-VR |
|---|---:|---:|---:|---:|
| Development 24, numero popup | 12 | 12 | 12 | 12 |
| Holdout 32, numero popup | 13 | 12 | 13 | 12 |

- Development: **zero cambiamenti** di vincitore in ogni variante.
- Holdout, caso 004: S2-V e S2-R selezionano «gli mando la scansione domattina» al posto della frase descrittiva sul commercialista.
- Holdout, caso 021: il solo veto S2-V esclude l'aspirazione vaga; il solo ranking S2-R **non** elimina il popup perché è l'unico candidato eleggibile.
- S2-VR produce sui set noti i cambiamenti di S2-V e nessuno aggiuntivo. Su questi esempi non è evidente un contributo incrementale della combinazione.

**Decisione:** nessuna promozione a nuovo selettore stabile su questa evidenza; progettazione completata. È necessario annotare nuove note prima del test, valutarle indipendentemente e misurare precisione, recall per nota e regressioni.
