# Fase 3 — Contratto

## Obiettivo

Creare contratti di interfaccia immutabili. Descrivere i dati, la loro gestione e le interazioni con i client. Fornire agli Agenti AI specifiche precise per ogni risorsa.

## Rischi da mitigare

- **Mismatch tra componenti**: frontend/backend disallineati su formati o endpoint.
- **Ridondanza**: stesse informazioni definite in modi diversi.
- **Scarsa efficienza**: query non ottimizzate, indici mancanti.

## Principi

- **Flusso informativo**: descrivere fonti dati, logiche di persistenza e gestione.
- **Presentazione**: elencare e descrivere le API di interazione (consumate e esposte).
- **Criteri di accettazione**: dare agli agenti un criterio di validazione del proprio lavoro.

---

## Protocollo Operativo

### Step 1: Contratti di Interfaccia — `API_SPEC.md`

Descrivere sia le interfacce consumate che quelle esposte.

**Contenuto** (vedi template `references/templates/api_spec.md`):
- Convenzioni generali (base URL, metodi HTTP, content-type)
- Formato risposta standard (successo/errore) con esempi JSON
- Per ogni endpoint:
  - Parametri in tabella (Nome, Tipo, Obbligatorio, Descrizione)
  - Risposta attesa con esempio JSON
  - Logica backend in passi numerati
  - Note transazionali se applicabili

**Regole**:
- Ogni endpoint deve avere almeno un esempio JSON di risposta.
- I parametri obbligatori devono essere esplicitamente marcati.
- Campi nascosti (es. `id` non visibili all'utente) documentati con nota esplicita.

**Standard di riferimento**: BAM Appendice A.3

### Step 2: Modellazione del Dominio Dati — `SCHEMA_REFERENCE.md`

Formalizzare la struttura della persistenza usando linguaggi dichiarativi e visuali.

**Contenuto** (vedi template `references/templates/schema_reference.md`):
- Diagramma ER in **Mermaid erDiagram** (visualizzabile in GitHub/GitLab)
- Definizione tabelle in **DBML** (Database Markup Language) — fonte autoritativa per colonne, tipi, vincoli, indici
- Dettaglio per tabella: volume stimato, strategia partizionamento, note operative

**Regole**:
- Il diagramma Mermaid e' obbligatorio e deve rappresentare tutte le relazioni.
- La definizione DBML e' la fonte autoritativa per la struttura.
- Le note DBML descrivono il significato di business, non il tipo tecnico.
- Per tabelle con volume > 10k record, indicare volume e strategia di indicizzazione.

**Standard di riferimento**: BAM Appendice A.7 (DBML + Mermaid erDiagram)

### Step 3: Riferimento Query — `QUERY_REFERENCE.md`

Raccogliere le operazioni di lettura/scrittura critiche o complesse come Gold Standard.

**Contenuto** (vedi template `references/templates/query_reference.md`):
- ID univoco per query: `Q-<MODULO>-<NUMERO>`
- Statement SQL con named parameters (`:nome`)
- Tabella parametri con tipo ed esempio
- Note di performance (indici, LIMIT, partizionamento)
- Raggruppamento transazionale esplicito

**Regole**:
- Mai valori hardcoded nello statement — solo named parameters.
- Volume tabelle indicato per orientare scelte di performance.
- Note performance obbligatorie per tabelle con volume significativo.

**Standard di riferimento**: BAM Appendice A.4

### Step 4: Elenco Globale dei Test — `EXPLAIN_TEST.md`

Elencare tutti i test suddivisi per area.

**Contenuto**:
- **Unit test**: test di singole unita' logiche
- **Integration test**: test di interazione tra componenti
- **System test**: test end-to-end del sistema
- **Acceptance test**: test derivati da ACCEPTANCE_CRITERIA.md

Ogni test deve avere:
- ID univoco
- Descrizione dello scenario
- Precondizioni
- Risultato atteso
- Area di appartenenza (unit/integration/system/acceptance)

Questi test servono prima agli Agenti per validare lo sviluppo, poi all'umano per accettare il progetto.

**Standard di riferimento**: BDD

---

## Artefatti

| File | Template | Standard |
|------|----------|----------|
| `API_SPEC.md` | `templates/api_spec.md` | BAM A.3 |
| `SCHEMA_REFERENCE.md` | `templates/schema_reference.md` | BAM A.7 (DBML + Mermaid) |
| `QUERY_REFERENCE.md` | `templates/query_reference.md` | BAM A.4 |
| `EXPLAIN_TEST.md` | — | BDD |

---

## Checkpoint

Al termine della fase, chiedi:

> "I contratti di interfaccia sono definiti: API, schema dati, query di riferimento e piano dei test. Procedo alla Fase 4 — Planning?"

NON procedere senza approvazione esplicita dell'umano.
