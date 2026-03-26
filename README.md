# Skills

**Versione:** 0.12.0
**Ultima modifica:** 2026-03-26

Repository dedicato allo sviluppo del modello architetturale **Blueprint Agentic Model (BAM)** e delle skill Claude Code che ne implementano il processo e le best practice di sviluppo software.

## Contenuto del repository

### 1. Blueprint Agentic Model (BAM)

Il BAM e' un paradigma metodologico per lo sviluppo software assistito da agenti AI generativi. La documentazione tecnica, strutturata secondo standard ingegneristici,
costituisce la fonte epistemica primaria (*single source of truth*) da cui gli agenti generano codice in modo autonomo e verificabile.

Il processo si articola in quattro fasi: **Brainstorming**, **Analisi e Design**, **Definizione del Contratto**, **Planning**.

| File                         | Descrizione                                       |
|------------------------------|---------------------------------------------------|
| `blueprint-agentic-model.md` | Documento principale che definisce il modello BAM |
| `bam_workflow.svg`           | Diagramma del workflow BAM                        |

### 2. Skill BAM per Claude Code

Trasposizione del modello BAM in una skill eseguibile da Claude Code, che orchestra l'intero ciclo di vita di un progetto software — dall'idea al blueprint pronto per l'implementazione.

```
cc-skills/bam-model-skill/
  SKILL.md                        # Definizione della skill
  references/
    phase1_brainstorming.md       # Guida fase 1
    phase2_analysis_design.md     # Guida fase 2
    phase3_contract.md            # Guida fase 3
    phase4_planning.md            # Guida fase 4
    templates/                    # Template per gli artefatti documentali
      api_spec.md
      aq_iterations.md
      execution_plan.md
      logging_strategy.md
      query_reference.md
      schema_reference.md
      test_environment.md
  scripts/
    bootstrap_bam_project.py      # Bootstrap di un nuovo progetto BAM
    generate_template.py          # Generazione template da libreria
```
Skill per il supporto a una generazione di documentazione coerente

| Skill                    | Ambito                                                                            |
|--------------------------|-----------------------------------------------------------------------------------|
| `ears-doc-skill`         | Specifica dei requisiti con il metodo EARS (Easy Approach to Requirements Syntax) |


### 3. Skill di sviluppo software Cartella `cc-skills/`

Skill per Claude Code che codificano le best practice di sviluppo per diversi linguaggi e ambiti.
Ogni skill si attiva autonomamente quando viene rilevato il contesto appropriato.

| Skill                    | Ambito                                                                                                                                                                                                        |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `coding-standards-skill` | Metodologia di sviluppo enterprise e framework di collaborazione AI. Governa *come* si scrive il codice — qualita', naming, sicurezza, pensiero critico. Opera a monte delle skill specifiche per linguaggio. |
| `go-dev-skill`           | Go 1.22+ — microservizi, concorrenza, gRPC, CLI, cloud-native                                                                                                                                                 |
| `php82-dev-skill`        | PHP 8.2+ — strict types, readonly, enum, PSR, PHPStan, OWASP                                                                                                                                                  |
| `postgresql16-dev-skill` | PostgreSQL 16 — schema design, migrazioni, ottimizzazione query, JSONB                                                                                                                                        |
| `ts-vue-dev-skill`       | TypeScript 5.x + Vue 3 — Composition API, Pinia, Vitest                                                                                                                                                       |

### 4. Bibliografia

Nella directory `bibbliografia/` sono raccolte alcune fonti di riferimento.

## Autore

**Mattia Costantini (Rancor)** — Senior IT Architect, Firstance s.r.l.

## Licenza


