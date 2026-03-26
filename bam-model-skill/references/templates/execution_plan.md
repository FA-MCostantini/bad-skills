# Template — EXECUTION_PLAN.md (BAM Appendice A.5)

Definisce la roadmap operativa per gli Agenti AI che eseguono la generazione del codice.
Suddivide il lavoro in fasi, assegna task a Agenti specifici, stabilisce dipendenze e checkpoint.

## Struttura

```markdown
# <nome progetto> — Piano di Esecuzione Multi-Agentico

**Goal:** <obiettivo complessivo del piano>

**Architecture:** <sintesi dell'architettura in una frase>

**Tech Stack:** <elenco delle tecnologie>

---

## Mappa delle Fasi e Dipendenze

<!-- Diagramma ASCII: --> = sequenziale, | = parallelo -->

```
Phase 1: <NOME> ──────────────────────
  Agent 1 (<SIGLA>)  →  Agent 2 (<SIGLA>)
                              │
Phase 2: <NOME> ────────────┬─┴─┬─────
  Agent 3 (<SIGLA>) | Agent 4 (<SIGLA>)
                         │
Phase 3: <NOME> ─────────┴────────────
  Agent 5 (<SIGLA>)
```

---

## Phase <N>: <Nome fase>

### Agent <N> — <SIGLA>

| Proprieta'       | Valore                                      |
|-------------------|---------------------------------------------|
| **Modello**       | <haiku | sonnet | opus>                     |
| **Tipo**          | <descrizione del tipo di lavoro>            |
| **Dipendenze**    | <Agent N completato | Nessuna>              |

**Docs da leggere:** `TECH_STACK.md`, `SCHEMA_REFERENCE.md`, ...

**Files:**
- Create: `<path/nuovo_file>`
- Modify: `<path/file_esistente>`

**Pre-check:** <condizioni da verificare prima di iniziare>

**Contesto per l'agente:**
<Descrizione dettagliata di cosa deve fare, perche' e come.
Includere vincoli specifici, pattern da seguire, riferimenti ai documenti.>

- [ ] **Step 1:** <azione specifica e verificabile>
- [ ] **Step 2:** <azione specifica e verificabile>
- [ ] **Step N:** Commit: `<tipo>(<scope>): <messaggio>`

---

<!-- Ripetere per ogni Agent -->

## Checkpoint — Fine Phase <N>

Validazione umana prima di procedere alla fase successiva.
Verificare:
- [ ] Tutti gli step degli Agent della fase sono completati
- [ ] I test pertinenti passano
- [ ] Il codice generato e' coerente con le specifiche
```

## Regole

- Il numero di Agenti per progetto e' compreso tra **3 e 7** salvo complessita' superiore.
- Ogni Agente ha un **modello** (haiku/sonnet/opus), un **tipo** di lavoro e **dipendenze** esplicite.
- **Docs da leggere**: i file del blueprint che l'Agente consulta *prima* di iniziare.
- **Files**: distinguere tra Create e Modify.
- Ogni step e' una **checkbox Markdown** (`- [ ]`) per tracciamento progresso.
- L'ultimo step di ogni Agente e' un **commit** con messaggio convenzionale.
- Le fasi raggruppano Agenti paralleli (`|`) o sequenziali (`→`).
- Tra fasi: **checkpoint umano** obbligatorio.
- Scelta modello: haiku per task ripetitivi/semplici, sonnet per task standard, opus per task architetturali complessi.
