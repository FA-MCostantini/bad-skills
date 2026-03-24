# php82-dev — Kiro Skill

PHP 8.2+ development specialist for enterprise-grade applications. Use when writing, reviewing, or refactoring PHP code, creating PHP classes, implementing design patterns in PHP, handling PHP error management, or working with PSR standards. Covers strict_types enforcement, readonly classes, enums, match expressions, constructor property promotion, PHPDoc rules, PHPStan level 8/9 compliance, structured error handling with PSR-3 logging, audit trails for financial systems, and OWASP security patterns. Activates autonomously when PHP code context is detected.

## Overview

This skill has been converted from Claude Code format to Kiro-optimized structure.
It leverages Kiro's native LSP capabilities and memory system.

## Quick Start

1. Load core rules:
   ```
   read_memory php82-dev/core-rules
   ```

2. Initialize LSP (if not done):
   ```
   /code init
   ```

3. Apply workflow from `memories/workflow.md`

## Structure

```
php82-dev/
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

project-dev-skill, ears-doc-skill, postgresql16-dev-skill

## Metadata

- **Domain**: language
- **Version**: 1.0.0
- **Author**: Mattia Costantini
