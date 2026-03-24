# php82-dev — Workflow



## Kiro-Specific Workflow

1. **Analyze**: Use LSP to understand codebase structure
   ```
   code search_symbols <relevant_term>
   code get_document_symbols <file_path>
   ```

2. **Load Context**: Load relevant memories
   ```
   read_memory php82-dev/core-rules
   read_memory php82-dev/patterns/<specific_pattern>
   ```

3. **Implement**: Use code intelligence for implementation
   - Navigate with `code goto_definition`
   - Find usages with `code find_references`
   - Refactor with `code rename_symbol`

4. **Validate**: Check against core rules checklist

## Memory Loading Strategy

| Scenario | Memory to Load |
|----------|----------------|
| Always | `php82-dev/core-rules` |
| Security concerns | `php82-dev/patterns/security` |
| Testing | `php82-dev/patterns/testing` |
| Complex patterns | `php82-dev/patterns/<specific>` |
