---
name: bad-model-skill
description: Blueprint Agentic Development — structured process for AI-assisted software projects. Orchestrates the full lifecycle from idea to implementation-ready blueprint through 4 phases (Brainstorming, Analysis/Design, Contract, Planning). Produces documentation artifacts that serve as the single source of truth for code generation. Use when starting any new project, feature, or significant evolution.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
metadata:
  author: Mattia Costantini
  version: "1.0.0"
  domain: process
  triggers: new project start blueprint planning architecture design requirements specification
  role: orchestrator
  scope: cross-cutting
  output-format: mixed
  autonomy: false
  related-skills: coding-standards-skill, ears-doc-skill, php82-dev-skill, postgresql16-dev-skill, ts-vue-dev-skill, go-dev-skill
---

# Blueprint Agentic Development (BAD)

Processo strutturato per lo sviluppo software assistito da Agenti AI.
La documentazione tecnica e' la **fonte epistemica primaria** (*single source of truth*) da cui gli Agenti generano codice in modo autonomo e verificabile.

> **Scope**: questa skill governa il *processo* — da idea a blueprint pronto.
> Per la fase di implementazione del codice vedi **coding-standards-skill**.

---

## Principi Fondamentali

1. **Docs-as-Code** — La documentazione e' sotto versioning, gestita come codice sorgente.
2. **Spec-as-Source** — Le specifiche sono la fonte unica; il codice ne e' una derivazione.
3. **Comprensione reciproca** — Non si accetta il primo risultato; si affina iterativamente.
4. **Contesto deterministico** — Contesto limitato, preciso e univoco riduce allucinazioni.
5. **Tracciabilita' del pensiero** — Documentare il *perche'*, non solo il *cosa*.

---

## Mappa delle Fasi

```
Fase 1: BRAINSTORMING ──────── Fase 2: ANALISI & DESIGN
  (Comprensione reciproca)       (Blueprint architetturale)
  PROJECT.md + AQ_ITERATIONS     SPEC, ACCEPTANCE, ADR, GLOSSARIO,
                                  LOGGING, TEST_ENV, DEPLOY
         │                                  │
         ▼                                  ▼
Fase 3: CONTRATTO ───────────── Fase 4: PLANNING
  (Interfacce e dati)             (Roadmap per agenti)
  API_SPEC, SCHEMA_REF,          EXECUTION_PLAN, README
  QUERY_REF, EXPLAIN_TEST
         │
         ▼
  ┌─────────────────────┐
  │ coding-standards-skill│ ← Implementazione codice
  │  + language skills   │
  └─────────────────────┘
```

---

## Protocollo di Esecuzione

### Regole generali

- **Checkpoint obbligatorio**: al termine di ogni fase, chiedi validazione all'umano. NON procedere senza approvazione esplicita.
- **Nessun codice**: durante le Fasi 1-4 non si scrive codice sorgente. Si producono solo artefatti documentali.
- **Iterazione**: se l'umano chiede modifiche, reitera la fase corrente prima di avanzare.

### Fase 1 — Brainstorming

**Obiettivo**: raggiungere comprensione reciproca ad alta confidenza.

Leggi `references/phase1_brainstorming.md` e segui il protocollo.

**Artefatti prodotti**: `PROJECT.md`, `AQ_ITERATIONS.md`

**Checkpoint**: *"Il PROJECT.md riflette la tua visione? Posso procedere all'analisi?"*

### Fase 2 — Analisi e Design

**Obiettivo**: costruire il blueprint architetturale — vincoli, requisiti, decisioni.

Leggi `references/phase2_analysis_design.md` e segui il protocollo.

**Artefatti prodotti**: `TECH_STACK.md`, `ACCEPTANCE_CRITERIA.md`, `ADR/`, `GLOSSARIO.md`, `LOGGING_STRATEGY.md`, `TEST_ENVIRONMENT.md`, `DEPLOY.md`

**Checkpoint**: *"Il blueprint architetturale e' completo. Vuoi validarlo prima di passare ai contratti?"*

### Fase 3 — Contratto

**Obiettivo**: definire contratti di interfaccia immutabili — dati, API, test.

Leggi `references/phase3_contract.md` e segui il protocollo.

**Artefatti prodotti**: `API_SPEC.md`, `SCHEMA_REFERENCE.md`, `QUERY_REFERENCE.md`, `EXPLAIN_TEST.md`

**Checkpoint**: *"I contratti di interfaccia sono definiti. Procedo alla pianificazione?"*

### Fase 4 — Planning

**Obiettivo**: definire la roadmap operativa per gli Agenti che genereranno il codice.

Leggi `references/phase4_planning.md` e segui il protocollo.

**Artefatti prodotti**: `EXECUTION_PLAN.md`, `README.md`

**Checkpoint**: *"Il piano di esecuzione e' pronto. Vuoi validarlo prima di avviare l'implementazione?"*

### Transizione all'implementazione

Completata la Fase 4 con validazione:
1. Attiva **coding-standards-skill** per la metodologia di codifica.
2. Le skill di linguaggio specifiche si attivano automaticamente in base allo stack tecnologico definito in `TECH_STACK.md`.
3. L'`EXECUTION_PLAN.md` guida l'ordine e l'assegnazione dei task agli Agenti.

---

## Evoluzione di un Progetto Esistente

Per modifiche su progetti gia' avviati con BAD:

1. Aggiorna `CHANGELOG.md` con le modifiche richieste.
2. Apri una nuova iterazione in `AQ_ITERATIONS.md` per chiarimenti.
3. Aggiorna la documentazione impattata.
4. Procedi con l'implementazione via coding-standards-skill.

Non e' necessario rieseguire l'intero processo per modifiche di minore entita'.

---

## Regola di Contesto

Se la conversazione supera i 20 scambi all'interno di una fase, rileggi il reference della fase corrente prima di procedere. Le istruzioni devono restare fresche nel contesto.

---

## Bootstrap Rapido

Per inizializzare la struttura documentale di un nuovo progetto:

```bash
python3 bad-model-skill/scripts/bootstrap_bad_project.py /path/to/project
```

Crea l'intera struttura di directory e file template pronti per essere compilati.

---

## Struttura Documentale Completa

| File | Fase | Scopo | Standard |
|------|------|-------|----------|
| `PROJECT.md` | 1 | Visione e obiettivi di business | Product Vision Template |
| `AQ_ITERATIONS.md` | 1 | Log Q&A iterativo umano-AI | BAD A.1 |
| `TECH_STACK.md` | 2 | Inventario tecnologico, vincoli infrastrutturali e non funzionali | RFC 2119 + Twelve-Factor App |
| `ACCEPTANCE_CRITERIA.md` | 2 | Criteri di accettazione per feature | Standard EARS |
| `ADR/` | 2 | Registro decisioni architetturali | Nygard ADR Format |
| `GLOSSARIO.md` | 2 | Linguaggio ubiquitario (DDD) | Domain-Driven Design |
| `LOGGING_STRATEGY.md` | 2 | Standard di osservabilita' | BAD A.2 |
| `TEST_ENVIRONMENT.md` | 2 | Strategia di test, ambienti, mock e dati | BAD A.6 |
| `DEPLOY.md` | 2 | Pipeline CI/CD e rilascio | DevOps Best Practices |
| `API_SPEC.md` | 3 | Contratti di interfaccia endpoint | BAD A.3 |
| `SCHEMA_REFERENCE.md` | 3 | Diagrammi ER (Mermaid) e definizione tabelle (DBML) | BAD A.7 |
| `QUERY_REFERENCE.md` | 3 | Query SQL critiche e Gold Standard | BAD A.4 |
| `EXPLAIN_TEST.md` | 3 | Elenco test per fase progettuale | Standard BDD |
| `EXECUTION_PLAN.md` | 4 | Roadmap multi-agentica | BAD A.5 |
| `CHANGELOG.md` | Evo | Modifiche richieste | Keep a Changelog |
| `README.md` | 4 | Presentazione progetto | Standard GitHub |
