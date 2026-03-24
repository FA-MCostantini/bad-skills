# Skills Converter — Claude Code to Kiro

Sistema automatico per convertire skills Claude Code in formato ottimizzato per Kiro CLI.

## Overview

Questo progetto contiene:
- **Agente AI** (`ai-converter-agent.md`) — Agente intelligente che analizza e decide
- **Agente rule-based** (`skill-converter-agent.md`) — Specifica con logica fissa
- **Script automatico** (`convert_skill.py`) — Implementazione rule-based veloce
- **Skills Claude Code** — Originali da convertire
- **Skills Kiro** (`kiro-skills/`) — Versioni convertite

## Due Modalità di Conversione

### 1. Script Automatico (Rule-Based) — Veloce

**Usa quando:**
- Skills standard con struttura nota
- Conversione batch di molte skills
- Vuoi velocità e automazione

**Limitazioni:**
- Pattern matching fisso su nomi file
- Non analizza il contenuto degli script
- Non si adatta a strutture non standard

```bash
./convert_skill.py ./php82-dev-skill ./kiro-skills/php82-dev php82-dev
./convert_all.sh  # Batch
```

### 2. Agente AI (Kiro) — Intelligente

**Usa quando:**
- Skill complessa o struttura non standard
- Vuoi analisi del contenuto, non solo nomi
- Skill scaricata da internet con logica custom
- Vuoi decisioni giustificate e documentate

**Vantaggi:**
- Legge e comprende il codice degli script
- Valuta ogni componente contestualmente
- Si adatta a qualsiasi struttura
- Documenta il ragionamento di ogni decisione

```
# In Kiro
read_file ai-converter-agent.md

# Poi chiedi
Convert ./custom-skill to ./kiro-skills/custom analyzing content deeply
```

## Quick Start

### Convertire una skill

```bash
./convert_skill.py <source_path> <target_path> <skill_name>
```

**Esempio:**
```bash
./convert_skill.py ./php82-dev-skill ./kiro-skills/php82-dev php82-dev
```

### Convertire tutte le skills

```bash
# PHP
./convert_skill.py ./php82-dev-skill ./kiro-skills/php82-dev php82-dev

# Go
./convert_skill.py ./go-dev-skill ./kiro-skills/go-dev go-dev

# TypeScript/Vue
./convert_skill.py ./ts-vue-dev-skill ./kiro-skills/ts-vue-dev ts-vue-dev

# PostgreSQL
./convert_skill.py ./postgresql16-dev-skill ./kiro-skills/postgresql16-dev postgresql16-dev

# Project Methodology
./convert_skill.py ./project-dev-skill ./kiro-skills/project-dev project-dev

# EARS Documentation
./convert_skill.py ./ears-doc-skill ./kiro-skills/ears-doc ears-doc
```

## Cosa fa il converter

### 1. ANALYZE
- Legge `SKILL.md` ed estrae metadata
- Identifica `references/` e `scripts/`
- Analizza struttura e contenuto

### 2. CLASSIFY
- **Elimina** script sostituibili da LSP (generate_class, generate_interface, etc.)
- **Mantiene** script essenziali (formattazione custom, bootstrap)
- **Separa** references in core vs patterns

### 3. EXTRACT
- Estrae regole non negoziabili
- Estrae workflow e checklist
- Identifica trigger e contesti d'uso

### 4. TRANSFORM
Genera struttura Kiro:
```
kiro-skills/<skill-name>/
├── README.md                    # Overview
├── USAGE.md                     # Guida d'uso con Kiro
├── CONVERSION_REPORT.md         # Dettagli conversione
├── memories/
│   ├── core-rules.md           # Regole essenziali
│   ├── workflow.md             # Metodologia
│   └── patterns/               # Pattern on-demand
│       ├── security.md
│       └── ...
└── scripts/                     # Solo script essenziali
    └── ...
```

### 5. DOCUMENT
- Genera report di conversione
- Documenta cosa è stato eliminato/mantenuto/trasformato
- Crea guida d'uso specifica per Kiro

## Differenze Claude Code vs Kiro

| Aspetto | Claude Code | Kiro |
|---------|-------------|------|
| **Attivazione** | Autonoma via trigger | Manuale via memories |
| **Code Intelligence** | Script Python | LSP nativo |
| **Navigazione** | Grep testuale | Semantic search |
| **Refactoring** | Manuale | LSP rename/references |
| **Tool** | Read/Edit/Write | fs_read/fs_write/code |

## Vantaggi della conversione

1. **LSP nativo** — Elimina bisogno di script di generazione
2. **Semantic search** — `code search_symbols` > grep
3. **Safe refactoring** — `rename_symbol` con find references
4. **Memories esplicite** — Controllo su cosa caricare
5. **Meno dipendenze** — Meno script Python da mantenere

## Struttura Output

Ogni skill convertita contiene:

### README.md
- Overview della skill
- Quick start
- Struttura files
- Metadata originale

### USAGE.md
- Come usare con Kiro
- Comandi LSP rilevanti
- Strategia di caricamento memories
- Esempi concreti

### CONVERSION_REPORT.md
- Cosa è stato eliminato (e perché)
- Cosa è stato mantenuto
- Cosa è stato trasformato
- Struttura finale

### memories/core-rules.md
- Regole non negoziabili
- Quality checklist
- Integrazione LSP
- Quando caricare altre memories

### memories/workflow.md
- Metodologia applicazione skill
- Workflow specifico Kiro
- Decision framework
- Memory loading strategy

### memories/patterns/
- Pattern specifici (security, testing, etc.)
- Caricati on-demand quando rilevanti

### scripts/
- Solo script NON sostituibili da LSP
- Formattazione custom
- Bootstrap/setup
- Tool specifici

## Usare le skills convertite con Kiro

### 1. Inizializza LSP (una volta per progetto)
```
/code init
```

### 2. Carica core rules della skill
```
read_memory php82-dev/core-rules
```

### 3. Usa LSP per navigazione
```
code search_symbols MyClass
code lookup_symbols MyClass MyInterface
code find_references MyMethod path/to/file.php
```

### 4. Carica pattern on-demand
```
read_memory php82-dev/patterns/security
```

### 5. Segui workflow
```
read_memory php82-dev/workflow
```

## Aggiungere nuove skills

Quando Claude Code rilascia nuove skills:

1. Scarica la skill in questa cartella
2. Esegui il converter:
   ```bash
   ./convert_skill.py ./new-skill ./kiro-skills/new-skill new-skill
   ```
3. Verifica il `CONVERSION_REPORT.md`
4. Testa con Kiro

## Agenti Converter

### Rule-Based Agent (`skill-converter-agent.md`)
- Logica fissa, pattern matching
- Veloce per skills standard
- Implementato in `convert_skill.py`

### AI Agent (`ai-converter-agent.md`)
- Analisi intelligente del contenuto
- Si adatta a qualsiasi struttura
- Usa Kiro per decisioni contestuali
- Documenta ragionamento

**Quando usare quale:**
- Skills standard note → Rule-based script
- Skills complesse/custom → AI agent in Kiro
- Batch conversion → Rule-based script
- Analisi approfondita → AI agent

## Files Principali

- `ai-converter-agent.md` — Agente AI intelligente (analizza contenuto)
- `skill-converter-agent.md` — Agente rule-based (pattern matching)
- `convert_skill.py` — Script di conversione automatica
- `convert_all.sh` — Batch conversion script
- `kiro-skills/` — Skills convertite (output)
- `*-skill/` — Skills Claude Code originali (input)

## Manutenzione

### Aggiornare una skill esistente
1. Aggiorna la versione Claude Code originale
2. Ri-esegui il converter
3. Verifica il diff nel CONVERSION_REPORT.md

### Personalizzare la conversione
Modifica `convert_skill.py`:
- `_classify()` — Logica keep/eliminate
- `_extract()` — Sezioni da estrarre
- `_transform()` — Struttura output

## Limitazioni

- Non converte automaticamente script complessi
- Richiede revisione manuale per edge cases
- Pattern di classificazione potrebbero necessitare tuning

## Contribuire

Per migliorare il converter:
1. Identifica pattern non gestiti
2. Aggiorna logica in `_classify()` o `_extract()`
3. Testa su tutte le skills esistenti
4. Documenta in questo README

## License

Same as original Claude Code skills.
