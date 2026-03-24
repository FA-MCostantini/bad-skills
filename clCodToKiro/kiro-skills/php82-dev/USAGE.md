# Using php82-dev with Kiro

## Quick Start

1. **Load core rules**:
   ```
   read_memory php82-dev/core-rules
   ```

2. **Initialize LSP** (if not already done):
   ```
   /code init
   ```

3. **Start working**:
   - Use LSP for navigation: `code search_symbols`, `code lookup_symbols`
   - Load patterns on-demand: `read_memory php82-dev/patterns/<name>`
   - Follow workflow from `memories/workflow.md`

## Memory Loading Strategy

### Always Load
- `php82-dev/core-rules` — Essential rules and LSP integration guide

### Load On-Demand
- `php82-dev/patterns/*` — Specific pattern libraries when relevant
- `php82-dev/workflow` — When planning complex implementations

## LSP Capabilities

Kiro's LSP replaces code generation scripts:

| Task | Kiro Command |
|------|--------------|
| Find symbols | `code search_symbols <name>` |
| Get symbol details | `code lookup_symbols <names>` |
| Find references | LSP find_references |
| Rename safely | LSP rename_symbol |
| Pattern search | `code pattern_search <pattern>` |

## Available Scripts

- `generate_php_middleware.py`
- `generate_php_enum.py`
- `generate_php_class.py`
- `generate_php_service.py`
- `generate_php_dto.py`
- `generate_php_test.py`


## Replaced by Kiro LSP

The following Claude Code scripts are no longer needed:

- ❌ `generate_repository.py` → Use LSP code intelligence


## Examples

### Example 1: Find and analyze a class
```
code search_symbols MyClass
code lookup_symbols MyClass --include-source
```

### Example 2: Load security patterns
```
read_memory php82-dev/patterns/security
```

### Example 3: Refactor with LSP
```
# Find all usages
find_referencing_symbols MyMethod path/to/file.ext

# Rename safely across codebase
rename_symbol MyMethod NewMethodName path/to/file.ext
```
