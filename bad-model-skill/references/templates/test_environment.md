# Template — TEST_ENVIRONMENT.md (BAD Appendice A.6)

Descrive la strategia e l'architettura degli ambienti di test in modo leggibile e validabile
anche da chi non conosce i dettagli implementativi. Il formato e' descrittivo-tabellare.

## Struttura

```markdown
# Ambiente di Test — <nome progetto>

---

## 1. Strategia di Test

<!-- Descrivere la filosofia generale: quali livelli di test
     vengono adottati e con quale scopo. -->

| Livello     | Scopo                              | Frequenza          |
|-------------|------------------------------------|--------------------|
| Unit        | Logica isolata, singola unita'     | Ad ogni commit     |
| Integration | Interazione tra componenti         | Ad ogni PR         |
| System      | End-to-end su stack completo       | Prima del rilascio |
| Acceptance  | Validazione criteri di accettazione| Prima del rilascio |

---

## 2. Ambienti

<!-- Per ogni ambiente: composizione, scopo, dati utilizzati. -->

| Ambiente    | Scopo                     | Composizione                         | Dati                         |
|-------------|---------------------------|--------------------------------------|------------------------------|
| Unit        | Test logica isolata       | Solo runtime, mock servizi esterni   | Fixture in-memory            |
| Integration | Test interazione          | Runtime + DB + message broker        | Seed da script SQL           |
| System      | Test end-to-end           | Stack completo containerizzato       | Copia anonimizzata staging   |

---

## 3. Servizi Mock

<!-- Per ogni servizio esterno simulato: strategia e motivazione. -->

| Servizio Esterno    | Strategia Mock                    | Motivazione                        |
|---------------------|-----------------------------------|------------------------------------|
| <nome servizio>     | <WireMock / container locale / …> | <perche' si usa un mock>           |

---

## 4. Dati di Test

<!-- Fonti, aggiornamento e volumi dei dataset di test. -->

| Dataset              | Fonte                  | Aggiornamento    | Volume         |
|----------------------|------------------------|------------------|----------------|
| <nome dataset>       | <script / dump / API>  | <frequenza>      | <N record>     |

---

## 5. Prerequisiti per Ambiente

<!-- Requisiti software e configurazioni necessarie
     per eseguire i test in locale o in CI. -->
```

## Regole

- Il documento DEVE essere comprensibile senza conoscenze implementative: un PM o un QA lead deve poter validare la strategia.
- Ogni ambiente deve indicare esplicitamente *quali dati* utilizza e *da dove* provengono.
- I servizi mock devono indicare la *motivazione* (es. evitare transazioni reali, velocita', isolamento).
- Le tabelle sono il formato primario; il testo narrativo e' usato solo per chiarimenti non tabulabili.
