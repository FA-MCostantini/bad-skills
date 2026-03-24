#!/usr/bin/env python3
"""
Skill Converter: Claude Code → Kiro
Converts Claude Code skills to Kiro-optimized format.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class SkillConverter:
    def __init__(self, source_path: str, target_path: str, skill_name: str):
        self.source = Path(source_path)
        self.target = Path(target_path)
        self.skill_name = skill_name
        self.eliminated = []
        self.kept = []
        self.transformed = []
        
    def convert(self):
        """Main conversion workflow."""
        print(f"🔄 Converting {self.skill_name}...")
        print(f"   Source: {self.source}")
        print(f"   Target: {self.target}\n")
        
        # Phase 1: Analyze
        skill_data = self._analyze()
        
        # Phase 2: Classify
        classification = self._classify(skill_data)
        
        # Phase 3: Extract
        extracted = self._extract(skill_data, classification)
        
        # Phase 4: Transform
        self._transform(extracted)
        
        # Phase 5: Document
        self._document(classification)
        
        print(f"\n✅ Conversion complete: {self.target}")
        
    def _analyze(self) -> Dict:
        """Phase 1: Analyze source skill structure."""
        print("📋 Phase 1: ANALYZE")
        
        skill_md = self.source / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {self.source}")
        
        with open(skill_md) as f:
            content = f.read()
        
        # Extract metadata from YAML frontmatter
        metadata = self._extract_metadata(content)
        
        # Find references and scripts
        refs_dir = self.source / "references"
        scripts_dir = self.source / "scripts"
        
        references = list(refs_dir.glob("*.md")) if refs_dir.exists() else []
        scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []
        
        print(f"   ✓ Found {len(references)} references")
        print(f"   ✓ Found {len(scripts)} scripts")
        
        return {
            "metadata": metadata,
            "content": content,
            "references": references,
            "scripts": scripts
        }
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract YAML frontmatter metadata."""
        if not content.startswith("---"):
            return {}
        
        end = content.find("---", 3)
        if end == -1:
            return {}
        
        yaml_block = content[3:end].strip()
        metadata = {}
        
        for line in yaml_block.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip('"')
        
        return metadata
    
    def _classify(self, skill_data: Dict) -> Dict:
        """Phase 2: Classify components (keep/eliminate/transform)."""
        print("\n🔍 Phase 2: CLASSIFY")
        
        classification = {
            "scripts_to_eliminate": [],
            "scripts_to_keep": [],
            "references_core": [],
            "references_patterns": []
        }
        
        # Classify scripts
        for script in skill_data["scripts"]:
            name = script.name
            if any(x in name for x in ["generate_class", "generate_interface", 
                                       "generate_component", "generate_repository",
                                       "generate_dto", "generate_enum", "generate_service",
                                       "generate_test", "generate_mock", "generate_handler"]):
                classification["scripts_to_eliminate"].append(script)
                self.eliminated.append(f"Script: {name} (replaced by LSP)")
            else:
                classification["scripts_to_keep"].append(script)
                self.kept.append(f"Script: {name}")
        
        # Classify references
        for ref in skill_data["references"]:
            name = ref.name.lower()
            if any(x in name for x in ["pattern", "security", "testing", "concurrency", 
                                       "generics", "database", "http", "errors", "logging"]):
                classification["references_patterns"].append(ref)
            else:
                classification["references_core"].append(ref)
        
        print(f"   ✓ Scripts to eliminate: {len(classification['scripts_to_eliminate'])}")
        print(f"   ✓ Scripts to keep: {len(classification['scripts_to_keep'])}")
        print(f"   ✓ Pattern references: {len(classification['references_patterns'])}")
        
        return classification
    
    def _extract(self, skill_data: Dict, classification: Dict) -> Dict:
        """Phase 3: Extract relevant content."""
        print("\n📤 Phase 3: EXTRACT")
        
        content = skill_data["content"]
        
        # Extract sections
        sections = {
            "core_rules": self._extract_section(content, ["Non-Negotiable Rules", "Hard Rules"]),
            "workflow": self._extract_section(content, ["Workflow", "Core Workflow", "Engagement Protocol"]),
            "checklist": self._extract_section(content, ["Quality Checklist", "Checklist"]),
            "triggers": skill_data["metadata"].get("triggers", ""),
            "description": skill_data["metadata"].get("description", "")
        }
        
        print(f"   ✓ Extracted core sections")
        
        return {
            "sections": sections,
            "classification": classification,
            "metadata": skill_data["metadata"]
        }
    
    def _extract_section(self, content: str, headers: List[str]) -> str:
        """Extract content under specific headers."""
        for header in headers:
            if f"## {header}" in content:
                start = content.find(f"## {header}")
                next_header = content.find("\n## ", start + 1)
                if next_header == -1:
                    next_header = content.find("\n---", start + 1)
                return content[start:next_header if next_header != -1 else len(content)].strip()
        return ""
    
    def _transform(self, extracted: Dict):
        """Phase 4: Transform to Kiro structure."""
        print("\n🔄 Phase 4: TRANSFORM")
        
        # Create directory structure
        self.target.mkdir(parents=True, exist_ok=True)
        (self.target / "memories").mkdir(exist_ok=True)
        (self.target / "memories" / "patterns").mkdir(exist_ok=True)
        
        # Generate README.md
        self._generate_readme(extracted)
        self.transformed.append("SKILL.md → README.md")
        
        # Generate memories/core-rules.md
        self._generate_core_rules(extracted)
        self.transformed.append("Core rules → memories/core-rules.md")
        
        # Generate memories/workflow.md
        self._generate_workflow(extracted)
        self.transformed.append("Workflow → memories/workflow.md")
        
        # Copy pattern references
        for ref in extracted["classification"]["references_patterns"]:
            target_file = self.target / "memories" / "patterns" / ref.name
            shutil.copy2(ref, target_file)
            self.transformed.append(f"{ref.name} → memories/patterns/{ref.name}")
        
        # Copy kept scripts
        if extracted["classification"]["scripts_to_keep"]:
            scripts_dir = self.target / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            for script in extracted["classification"]["scripts_to_keep"]:
                shutil.copy2(script, scripts_dir / script.name)
                os.chmod(scripts_dir / script.name, 0o755)
        
        # Generate USAGE.md
        self._generate_usage(extracted)
        self.transformed.append("Generated USAGE.md")
        
        print(f"   ✓ Generated {len(self.transformed)} files")
    
    def _generate_readme(self, extracted: Dict):
        """Generate README.md."""
        metadata = extracted["metadata"]
        content = f"""# {self.skill_name} — Kiro Skill

{metadata.get('description', '')}

## Overview

This skill has been converted from Claude Code format to Kiro-optimized structure.
It leverages Kiro's native LSP capabilities and memory system.

## Quick Start

1. Load core rules:
   ```
   read_memory {self.skill_name}/core-rules
   ```

2. Initialize LSP (if not done):
   ```
   /code init
   ```

3. Apply workflow from `memories/workflow.md`

## Structure

```
{self.skill_name}/
├── README.md              # This file
├── USAGE.md              # Detailed usage guide
├── CONVERSION_REPORT.md  # Conversion details
├── memories/
│   ├── core-rules.md    # Essential rules (always load)
│   ├── workflow.md      # Methodology
│   └── patterns/        # On-demand patterns
└── scripts/             # Essential scripts only
```

## Related Skills

{metadata.get('related-skills', 'None specified')}

## Metadata

- **Domain**: {metadata.get('domain', 'N/A')}
- **Version**: {metadata.get('version', 'N/A')}
- **Author**: {metadata.get('author', 'N/A')}
"""
        
        with open(self.target / "README.md", "w") as f:
            f.write(content)
    
    def _generate_core_rules(self, extracted: Dict):
        """Generate memories/core-rules.md."""
        sections = extracted["sections"]
        metadata = extracted["metadata"]
        
        content = f"""# {self.skill_name} — Core Rules

## Context

Use this memory when: {metadata.get('triggers', 'working with relevant code')}

{sections.get('core_rules', '## Rules\n\n(No specific rules extracted)')}

{sections.get('checklist', '')}

## LSP Integration

Kiro's native LSP replaces many code generation scripts:

- **Symbol search**: `code search_symbols <name>` — Find classes, functions, methods
- **Symbol lookup**: `code lookup_symbols <names>` — Get detailed symbol info
- **Pattern search**: `code pattern_search <pattern>` — AST-based code search
- **Find references**: Use LSP find_references tool
- **Rename symbol**: Use LSP rename_symbol tool

## Related Memories

Load additional patterns when needed:
- `{self.skill_name}/patterns/*` — Specific pattern libraries

## Critical Reminders

- Leverage LSP for code navigation and refactoring
- Load pattern memories on-demand, not upfront
- Use `code` tool for semantic understanding, `grep` for text search
"""
        
        with open(self.target / "memories" / "core-rules.md", "w") as f:
            f.write(content)
    
    def _generate_workflow(self, extracted: Dict):
        """Generate memories/workflow.md."""
        sections = extracted["sections"]
        
        content = f"""# {self.skill_name} — Workflow

{sections.get('workflow', '## Workflow\n\n(No specific workflow extracted)')}

## Kiro-Specific Workflow

1. **Analyze**: Use LSP to understand codebase structure
   ```
   code search_symbols <relevant_term>
   code get_document_symbols <file_path>
   ```

2. **Load Context**: Load relevant memories
   ```
   read_memory {self.skill_name}/core-rules
   read_memory {self.skill_name}/patterns/<specific_pattern>
   ```

3. **Implement**: Use code intelligence for implementation
   - Navigate with `code goto_definition`
   - Find usages with `code find_references`
   - Refactor with `code rename_symbol`

4. **Validate**: Check against core rules checklist

## Memory Loading Strategy

| Scenario | Memory to Load |
|----------|----------------|
| Always | `{self.skill_name}/core-rules` |
| Security concerns | `{self.skill_name}/patterns/security` |
| Testing | `{self.skill_name}/patterns/testing` |
| Complex patterns | `{self.skill_name}/patterns/<specific>` |
"""
        
        with open(self.target / "memories" / "workflow.md", "w") as f:
            f.write(content)
    
    def _generate_usage(self, extracted: Dict):
        """Generate USAGE.md."""
        classification = extracted["classification"]
        
        scripts_section = ""
        if classification["scripts_to_keep"]:
            scripts_section = "\n## Available Scripts\n\n"
            for script in classification["scripts_to_keep"]:
                scripts_section += f"- `{script.name}`\n"
        
        eliminated_section = "\n## Replaced by Kiro LSP\n\n"
        eliminated_section += "The following Claude Code scripts are no longer needed:\n\n"
        for script in classification["scripts_to_eliminate"]:
            eliminated_section += f"- ❌ `{script.name}` → Use LSP code intelligence\n"
        
        content = f"""# Using {self.skill_name} with Kiro

## Quick Start

1. **Load core rules**:
   ```
   read_memory {self.skill_name}/core-rules
   ```

2. **Initialize LSP** (if not already done):
   ```
   /code init
   ```

3. **Start working**:
   - Use LSP for navigation: `code search_symbols`, `code lookup_symbols`
   - Load patterns on-demand: `read_memory {self.skill_name}/patterns/<name>`
   - Follow workflow from `memories/workflow.md`

## Memory Loading Strategy

### Always Load
- `{self.skill_name}/core-rules` — Essential rules and LSP integration guide

### Load On-Demand
- `{self.skill_name}/patterns/*` — Specific pattern libraries when relevant
- `{self.skill_name}/workflow` — When planning complex implementations

## LSP Capabilities

Kiro's LSP replaces code generation scripts:

| Task | Kiro Command |
|------|--------------|
| Find symbols | `code search_symbols <name>` |
| Get symbol details | `code lookup_symbols <names>` |
| Find references | LSP find_references |
| Rename safely | LSP rename_symbol |
| Pattern search | `code pattern_search <pattern>` |
{scripts_section}
{eliminated_section}

## Examples

### Example 1: Find and analyze a class
```
code search_symbols MyClass
code lookup_symbols MyClass --include-source
```

### Example 2: Load security patterns
```
read_memory {self.skill_name}/patterns/security
```

### Example 3: Refactor with LSP
```
# Find all usages
find_referencing_symbols MyMethod path/to/file.ext

# Rename safely across codebase
rename_symbol MyMethod NewMethodName path/to/file.ext
```
"""
        
        with open(self.target / "USAGE.md", "w") as f:
            f.write(content)
    
    def _document(self, classification: Dict):
        """Phase 5: Generate conversion report."""
        print("\n📝 Phase 5: DOCUMENT")
        
        report = f"""# Conversion Report: {self.skill_name}

## Summary

- **Source**: {self.source}
- **Target**: {self.target}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Changes Made

### Eliminated (replaced by LSP)

"""
        for item in self.eliminated:
            report += f"- {item}\n"
        
        report += "\n### Kept\n\n"
        for item in self.kept:
            report += f"- {item}\n"
        
        report += "\n### Transformed\n\n"
        for item in self.transformed:
            report += f"- {item}\n"
        
        report += f"""

## Memory Structure

```
{self.skill_name}/
├── README.md
├── USAGE.md
├── CONVERSION_REPORT.md
├── memories/
│   ├── core-rules.md
│   ├── workflow.md
│   └── patterns/
"""
        
        for ref in classification["references_patterns"]:
            report += f"│       ├── {ref.name}\n"
        
        if classification["scripts_to_keep"]:
            report += "└── scripts/\n"
            for script in classification["scripts_to_keep"]:
                report += f"    ├── {script.name}\n"
        
        report += "```\n\n## Usage Instructions\n\nSee USAGE.md in output directory.\n"
        
        with open(self.target / "CONVERSION_REPORT.md", "w") as f:
            f.write(report)
        
        print(f"   ✓ Generated conversion report")


def main():
    if len(sys.argv) != 4:
        print("Usage: convert_skill.py <source_path> <target_path> <skill_name>")
        print("\nExample:")
        print("  ./convert_skill.py ./php82-dev-skill ./kiro-skills/php82-dev php82-dev")
        sys.exit(1)
    
    source = sys.argv[1]
    target = sys.argv[2]
    skill_name = sys.argv[3]
    
    converter = SkillConverter(source, target, skill_name)
    converter.convert()


if __name__ == "__main__":
    main()
