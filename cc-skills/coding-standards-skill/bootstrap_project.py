#!/usr/bin/env python3
import os
import sys

AQ_TEMPLATE = """# Iterazione Domande & Risposte
Questo file traccia tutte le iterazioni di domande e risposte tra l'analisi e l'utente.

**Stati possibili:**
- **APERTA**: domanda in attesa di risposta
- **RISOLTA**: risposta ricevuta e validata
- **IN ATTESA**: risposta parziale, serve approfondimento
- **SUPERATA**: domanda non più rilevante per il progetto

## Iterazione N - Punti da affrontare M
| ID | Domanda | Risposta | Stato |
|----|---------|----------|-------|
"""

README_TEMPLATE = """# Project Name

## Overview
Brief description of the project.

## Requirements

## Installation

## Usage

## Documentation
See `/docs` for detailed documentation.
"""

DOCS_FILES = {
    "ACCEPTANCE_CRITERIA.md": "",
    "API_CONTRACT.md": "",
    "DEPLOY.md": "",
    "GLOSSARIO.md": "",
    "QUERY_REFERENCE.md": "",
    "SCHEMA_REFERENCE.md": "",
    "SPEC_REQUISITI.md": "",
    "TEST_ENVIRONMENT.md": ""
}

def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    if not os.path.isdir(project_root):
        print(f"Error: {project_root} is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    # Create AQ_INTERACTION.md
    aq_file = os.path.join(project_root, "AQ_INTERACTION.md")
    if not os.path.exists(aq_file):
        with open(aq_file, "w", encoding="utf-8") as f:
            f.write(AQ_TEMPLATE)
        print(f"Created: {aq_file}")
    else:
        print(f"Skipped: {aq_file} (already exists)")
    
    # Create README.md
    readme_file = os.path.join(project_root, "README.md")
    if not os.path.exists(readme_file):
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(README_TEMPLATE)
        print(f"Created: {readme_file}")
    else:
        print(f"Skipped: {readme_file} (already exists)")
    
    # Create docs directory
    docs_dir = os.path.join(project_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    print(f"Created: {docs_dir}/")
    
    # Create documentation files
    for filename, content in DOCS_FILES.items():
        doc_file = os.path.join(docs_dir, filename)
        if not os.path.exists(doc_file):
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created: {doc_file}")
        else:
            print(f"Skipped: {doc_file} (already exists)")

if __name__ == "__main__":
    main()
