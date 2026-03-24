# Fase 2 — Analisi e Design

## Obiettivo

Costruire il blueprint architetturale: transizione dalla comprensione del dominio alla definizione dei vincoli ingegneristici. Questo blueprint limita il campo d'azione dell'AI a parametri precisi, garantendo codice manutenibile e scalabile.

## Principi

- **Ridurre arbitrarieta' architetturale**: imporre pattern specifici (Clean Architecture, Hexagonal, SOLID).
- **Validazione deterministica**: fornire criteri di accettazione (EARS) per test automatici.
- **Chiarezza e leggibilita'**: tabelle, grafici, struttura esplicita.
- **Mitigare il debito intellettuale**: la documentazione deve essere chiara perche' il codice verra' generato da essa.

---

## Protocollo Operativo

Genera i seguenti artefatti **in sequenza**. Per ogni artefatto, consulta il template corrispondente in `references/templates/`.

### Step 1: Inventario Tecnologico — `TECH_STACK.md`

Inventario delle dipendenze tecnologiche, vincoli infrastrutturali e non funzionali. Questo documento NON contiene requisiti funzionali (che vanno in ACCEPTANCE_CRITERIA.md) ne' decisioni architetturali (che vanno in ADR/).

**Contenuto**:
- Stack tecnologico (linguaggi, framework, versioni)
- Requisiti infrastrutturali (OS, container, servizi cloud)
- Vincoli di performance, sicurezza, compliance
- Requisiti non funzionali (disponibilita', scalabilita', backup)

**Linguaggio**: usa le keyword RFC 2119 (MUST, SHOULD, MAY) per esprimere l'obbligatorieta' dei vincoli.
**Principi infrastrutturali**: segui le linee guida Twelve-Factor App.

**Standard di riferimento**: RFC 2119 + Twelve-Factor App

### Step 2: Criteri di Accettazione — `ACCEPTANCE_CRITERIA.md`

Ogni requisito funzionale tradotto in clausole logiche EARS.

**Azione**: delega a **ears-doc-skill** per la generazione in sintassi EARS.

> "Questo artefatto richiede la sintassi EARS. Attivo ears-doc-skill per la generazione."

**Standard di riferimento**: Easy Approach to Requirements Syntax (EARS)

### Step 3: Decisioni Architetturali — `ADR/`

*(Opzionale ma raccomandato per ogni bivio tecnologico significativo)*

Per ogni decisione (es. scelta DB, strategia autenticazione, pattern architetturale):
- Crea un file `ADR/NNNN-titolo-decisione.md`
- Formato Nygard: Contesto, Decisione, Alternative scartate, Conseguenze

**Standard di riferimento**: Nygard ADR Format (2011)

### Step 4: Glossario — `GLOSSARIO.md`

Linguaggio Ubiquitario (DDD): allineamento terminologico per evitare che l'AI usi sinonimi diversi per lo stesso concetto di business nel codice.

**Contenuto**:
- Termine → Definizione → Contesto d'uso
- Acronimi e abbreviazioni
- Concetti di business con esempi

**Standard di riferimento**: Domain-Driven Design (Evans, 2003)

### Step 5: Strategia di Logging — `LOGGING_STRATEGY.md`

Definizione della strategia di osservabilita'.

**Contenuto**: vedi template `references/templates/logging_strategy.md`
- Livelli di log e uso
- Canali con destinazione e formato JSON
- Formato risposte API
- Regole di sicurezza
- Policy di retention

**Standard di riferimento**: BAD Appendice A.2

### Step 6: Ambiente di Test — `TEST_ENVIRONMENT.md`

Strategia e architettura degli ambienti di test. Il documento deve essere leggibile e validabile anche da chi non conosce i dettagli implementativi.

**Contenuto**: vedi template `references/templates/test_environment.md`
- Strategia di test (livelli, scopi, frequenza)
- Ambienti (composizione, dati per ambiente)
- Servizi mock (strategia e motivazione)
- Dati di test (fonti, aggiornamento, volumi)
- Prerequisiti per ambiente

**Formato**: descrittivo-tabellare — le tabelle sono il formato primario.

**Standard di riferimento**: BAD Appendice A.6

### Step 7: Scenari di Rilascio — `DEPLOY.md`

Processi per il rilascio operativo.

**Contenuto**:
- Requisiti di ambiente (produzione, staging)
- Passaggi di installazione e configurazione
- Pipeline CI/CD
- Procedura di rollback
- Checklist pre/post deployment

---

## Artefatti

| File | Template | Standard |
|------|----------|----------|
| `TECH_STACK.md` | — | RFC 2119 + Twelve-Factor App |
| `ACCEPTANCE_CRITERIA.md` | — (usa ears-doc-skill) | EARS |
| `ADR/NNNN-*.md` | Nygard format | Nygard ADR |
| `GLOSSARIO.md` | — | DDD |
| `LOGGING_STRATEGY.md` | `templates/logging_strategy.md` | BAD A.2 |
| `TEST_ENVIRONMENT.md` | `templates/test_environment.md` | BAD A.6 |
| `DEPLOY.md` | — | DevOps |

---

## Checkpoint

Al termine della fase, chiedi:

> "Il blueprint architetturale e' completo: requisiti, criteri di accettazione, decisioni architetturali, glossario, logging, test environment e deploy. Vuoi validarlo prima di passare alla Fase 3 — Contratto?"

NON procedere senza approvazione esplicita dell'umano.
