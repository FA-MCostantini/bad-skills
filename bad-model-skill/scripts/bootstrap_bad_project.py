#!/usr/bin/env python3
"""
Bootstrap BAD Project Structure.

Creates the complete documentation directory structure
for a Blueprint Agentic Development project.

Usage:
    python3 bootstrap_bad_project.py /path/to/project [project_name]
"""
import os
import sys
from datetime import datetime


PROJECT_TEMPLATE = """# {project_name}

## Visione

<Descrizione della visione del progetto>

## Obiettivi di Business

1. <Obiettivo 1>
2. <Obiettivo 2>

## Esperienza Utente Attesa

<Descrizione dell'esperienza utente>

## Contesto Applicativo

- **Dominio**: <dominio di business>
- **Utenti target**: <chi usera' il sistema>
- **Volume atteso**: <dimensionamento>

## Contesto Operativo

- **Ambiente**: <produzione, staging, sviluppo>
- **Infrastruttura**: <cloud, on-premise, ibrida>
- **Integrazioni**: <sistemi esterni>

## Vincoli Noti

- <Vincolo 1>
- <Vincolo 2>

## Perimetro Funzionale

### Cosa FA il sistema

- <Funzionalita' 1>

### Cosa NON FA il sistema

- <Esclusione 1>
"""

AQ_TEMPLATE = """# Iterazione Domande & Risposte

Progetto: **{project_name}** — <descrizione breve>
Documento di riferimento: `PROJECT.md`

---

## Iterazione 1 — Comprensione Iniziale

### AREA A — <Nome area tematica>

| ID   | Domanda | Risposta | Stato  |
|------|---------|----------|--------|
| A.01 | ...     | ...      | APERTO |
"""

TECH_STACK_TEMPLATE = """# Tech Stack — {project_name}

Standard di riferimento: **RFC 2119 + Twelve-Factor App**

Le keyword MUST, SHOULD, MAY seguono la semantica definita in RFC 2119.

---

## 1. Stack Tecnologico

| Componente | Tecnologia | Versione | Obbligatorieta' |
|------------|------------|----------|------------------|
| Linguaggio | ...        | ...      | MUST             |
| Framework  | ...        | ...      | MUST             |
| Database   | ...        | ...      | MUST             |

## 2. Requisiti Infrastrutturali

<!-- Descrivere usando MUST/SHOULD/MAY -->

## 3. Vincoli Non Funzionali

### 3.1 Performance
### 3.2 Sicurezza
### 3.3 Disponibilita'
### 3.4 Scalabilita'

## 4. Vincoli di Compliance

<!-- GDPR, OWASP, normative di settore -->
"""

ACCEPTANCE_CRITERIA_TEMPLATE = """# Criteri di Accettazione — {project_name}

Standard di riferimento: **EARS (Easy Approach to Requirements Syntax)**

---

<!-- Generare con ears-doc-skill -->

## Feature: <Nome feature>

### AC-001: <Titolo criterio>

**EARS**: <clausola EARS>

**Scenario**:
- **Given**: <precondizione>
- **When**: <azione>
- **Then**: <risultato atteso>
"""

GLOSSARIO_TEMPLATE = """# Glossario — {project_name}

Standard di riferimento: **Domain-Driven Design — Ubiquitous Language**

---

| Termine | Definizione | Contesto d'Uso | Note |
|---------|-------------|-----------------|------|
| ...     | ...         | ...             | ...  |
"""

LOGGING_STRATEGY_TEMPLATE = """# Strategia di Logging — {project_name}

Formato di riferimento: **Structured JSON Logging**
Standard di riferimento: **BAD Appendice A.2**

---

## 1. Livelli di log

| Livello   | Uso                                    | Esempio                            |
|-----------|----------------------------------------|------------------------------------|
| `ERROR`   | Errore che impedisce il completamento  | ...                                |
| `WARNING` | Situazione anomala ma gestita          | ...                                |
| `INFO`    | Azione di business completata          | ...                                |
| `DEBUG`   | Dettaglio tecnico (solo sviluppo)      | ...                                |

## 2. Canali di log

## 3. Formato risposta

## 4. Sicurezza dei log

| Regola                              | Applicazione |
|-------------------------------------|--------------|

## 5. Retention

| Canale | Retention |
|--------|-----------|
"""

TEST_ENVIRONMENT_TEMPLATE = """# Ambiente di Test — {project_name}

Standard di riferimento: **BAD Appendice A.6**

---

## 1. Strategia di Test

| Livello     | Scopo                              | Frequenza          |
|-------------|------------------------------------|--------------------|
| Unit        | Logica isolata, singola unita'     | Ad ogni commit     |
| Integration | Interazione tra componenti         | Ad ogni PR         |
| System      | End-to-end su stack completo       | Prima del rilascio |
| Acceptance  | Validazione criteri di accettazione| Prima del rilascio |

## 2. Ambienti

| Ambiente    | Scopo                     | Composizione                         | Dati                         |
|-------------|---------------------------|--------------------------------------|------------------------------|

## 3. Servizi Mock

| Servizio Esterno    | Strategia Mock                    | Motivazione                        |
|---------------------|-----------------------------------|------------------------------------|

## 4. Dati di Test

| Dataset              | Fonte                  | Aggiornamento    | Volume         |
|----------------------|------------------------|------------------|----------------|

## 5. Prerequisiti per Ambiente
"""

DEPLOY_TEMPLATE = """# Scenari di Rilascio — {project_name}

---

## 1. Requisiti di Ambiente

| Ambiente   | Descrizione | URL |
|------------|-------------|-----|
| Produzione | ...         | ... |
| Staging    | ...         | ... |

## 2. Pipeline CI/CD

## 3. Procedura di Deploy

1. <Step 1>
2. <Step 2>

## 4. Procedura di Rollback

1. <Step 1>
2. <Step 2>

## 5. Checklist Pre-Deploy

- [ ] Test passano
- [ ] Migration eseguite
- [ ] Configurazione verificata
"""

API_SPEC_TEMPLATE = """# Specifica API — {project_name}

Formato: **Endpoint-Action Reference**
Standard di riferimento: **BAD Appendice A.3**

---

## 1. Convenzioni generali

### 1.1 Base URL

### 1.2 Formato richiesta

### 1.3 Formato risposta
"""

SCHEMA_REFERENCE_TEMPLATE = """# Schema Reference — {project_name}

Standard di riferimento: **BAD Appendice A.7 (DBML + Mermaid erDiagram)**

---

## 1. Diagramma ER

```mermaid
erDiagram
    %% Definire le entita' e le relazioni
```

## 2. Definizione Tabelle (DBML)

```dbml
// Definizione dichiarativa delle tabelle
// Fonte autoritativa per colonne, tipi, vincoli e indici
```

## 3. Dettaglio per Tabella

### <nome_tabella>

**Volume stimato**: <N record>
**Strategia partizionamento**: <se applicabile>
**Note operative**: <vincoli di business, regole di cancellazione>
"""

QUERY_REFERENCE_TEMPLATE = """# Query Reference — {project_name}

Standard di riferimento: **BAD Appendice A.4**

Questo documento raccoglie le query SQL critiche o complesse,
organizzate per modulo.

---
"""

EXPLAIN_TEST_TEMPLATE = """# Piano dei Test — {project_name}

Standard di riferimento: **BDD**

---

## Unit Test

| ID | Descrizione | Precondizioni | Risultato Atteso |
|----|-------------|---------------|------------------|

## Integration Test

| ID | Descrizione | Precondizioni | Risultato Atteso |
|----|-------------|---------------|------------------|

## System Test

| ID | Descrizione | Precondizioni | Risultato Atteso |
|----|-------------|---------------|------------------|

## Acceptance Test

| ID | Rif. AC | Descrizione | Precondizioni | Risultato Atteso |
|----|---------|-------------|---------------|------------------|
"""

EXECUTION_PLAN_TEMPLATE = """# {project_name} — Piano di Esecuzione Multi-Agentico

**Goal:** <obiettivo complessivo>

**Architecture:** <sintesi architettura>

**Tech Stack:** <elenco tecnologie>

Standard di riferimento: **BAD Appendice A.5**

---

## Mappa delle Fasi e Dipendenze

```
Phase 1: ...
```

---
"""

CHANGELOG_TEMPLATE = """# Changelog — {project_name}

Formato: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [Unreleased]

### Added
### Changed
### Fixed
### Removed
"""

README_TEMPLATE = """# {project_name}

## Overview

<Descrizione del progetto>

## Requisiti di Sistema

## Installazione

## Uso Rapido

## Documentazione

La documentazione completa si trova nella cartella `docs/`:

| Documento | Descrizione |
|-----------|-------------|
| `PROJECT.md` | Visione e obiettivi |
| `docs/TECH_STACK.md` | Inventario tecnologico e vincoli |
| `docs/ACCEPTANCE_CRITERIA.md` | Criteri di accettazione |
| `docs/API_SPEC.md` | Specifiche API |
| `docs/SCHEMA_REFERENCE.md` | Schema database |

## Licenza
"""


# Files organized by BAD phase
PHASE_1_FILES = {
    "PROJECT.md": PROJECT_TEMPLATE,
    "AQ_ITERATIONS.md": AQ_TEMPLATE,
}

PHASE_2_FILES = {
    "docs/TECH_STACK.md": TECH_STACK_TEMPLATE,
    "docs/ACCEPTANCE_CRITERIA.md": ACCEPTANCE_CRITERIA_TEMPLATE,
    "docs/GLOSSARIO.md": GLOSSARIO_TEMPLATE,
    "docs/LOGGING_STRATEGY.md": LOGGING_STRATEGY_TEMPLATE,
    "docs/TEST_ENVIRONMENT.md": TEST_ENVIRONMENT_TEMPLATE,
    "docs/DEPLOY.md": DEPLOY_TEMPLATE,
}

PHASE_3_FILES = {
    "docs/API_SPEC.md": API_SPEC_TEMPLATE,
    "docs/SCHEMA_REFERENCE.md": SCHEMA_REFERENCE_TEMPLATE,
    "docs/QUERY_REFERENCE.md": QUERY_REFERENCE_TEMPLATE,
    "docs/EXPLAIN_TEST.md": EXPLAIN_TEST_TEMPLATE,
}

PHASE_4_FILES = {
    "docs/EXECUTION_PLAN.md": EXECUTION_PLAN_TEMPLATE,
    "CHANGELOG.md": CHANGELOG_TEMPLATE,
    "README.md": README_TEMPLATE,
}


def create_file(filepath, content, project_name):
    """Create a file if it doesn't exist, with project name substitution."""
    if os.path.exists(filepath):
        print(f"  Skipped: {filepath} (already exists)")
        return False

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    formatted_content = content.format(project_name=project_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(formatted_content)
    print(f"  Created: {filepath}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: bootstrap_bad_project.py <project_root> [project_name]")
        print("  project_root: path to the project directory")
        print("  project_name: name of the project (default: directory name)")
        sys.exit(1)

    project_root = os.path.abspath(sys.argv[1])
    project_name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(project_root)

    if not os.path.isdir(project_root):
        print(f"Error: {project_root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    print(f"\nBootstrapping BAD project: {project_name}")
    print(f"Directory: {project_root}")
    print(f"{'=' * 50}")

    # Create ADR directory
    adr_dir = os.path.join(project_root, "docs", "ADR")
    os.makedirs(adr_dir, exist_ok=True)
    print(f"  Created: {adr_dir}/")

    created_count = 0
    skipped_count = 0

    all_phases = [
        ("Phase 1 — Brainstorming", PHASE_1_FILES),
        ("Phase 2 — Analisi & Design", PHASE_2_FILES),
        ("Phase 3 — Contratto", PHASE_3_FILES),
        ("Phase 4 — Planning", PHASE_4_FILES),
    ]

    for phase_name, files in all_phases:
        print(f"\n{phase_name}:")
        for relative_path, template in files.items():
            filepath = os.path.join(project_root, relative_path)
            if create_file(filepath, template, project_name):
                created_count += 1
            else:
                skipped_count += 1

    print(f"\n{'=' * 50}")
    print(f"Done: {created_count} created, {skipped_count} skipped")
    print(f"\nNext step: edit PROJECT.md with your project vision,")
    print(f"then run bad-model-skill Phase 1 (Brainstorming).")


if __name__ == "__main__":
    main()
