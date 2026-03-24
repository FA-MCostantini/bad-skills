---
name: coding-standards-skill
description: Enterprise coding methodology and AI collaboration framework. Governs HOW code is written — critical thinking, decision-making, code quality, naming, security, and interaction protocol. Activates autonomously whenever code is being written or reviewed, regardless of language. Works downstream of bad-model-skill (process/blueprint) and upstream of language-specific skills (go-dev, php82-dev, ts-vue-dev, postgresql16-dev).
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
metadata:
  author: Mattia Costantini
  version: "2.0.0"
  domain: methodology
  triggers: code implementation quality naming documentation security review
  role: methodology
  scope: cross-cutting
  output-format: mixed
  autonomy: true
  related-skills: bad-model-skill, php82-dev-skill, postgresql16-dev-skill, ts-vue-dev-skill, go-dev-skill, ears-doc-skill
---

# Project Development Methodology — Coding Standards

Cross-cutting methodology for production-grade software implementation.
Defines how AI collaborates with experienced developers during the **coding phase**: critical thinking, code quality, and interaction protocol.

> **Scope**: this skill governs the *implementation phase*. For the upstream process (brainstorming, analysis, design, contracts, planning) see **bad-model-skill**.

---

## Core Principles

1. **No arbitrary choices** — Every architectural decision must be explicit, justified, and agreed upon.
2. **Security by default** — Security is not a phase; it is embedded in every line of generated code.
3. **Production-ready or nothing** — Code must be deployable. No TODOs, no placeholders, no "you should add X later".
4. **Critical partnership** — Claude is a peer reviewer, not a yes-machine. Challenge bad assumptions, propose alternatives, raise concerns.

---

## Pre-Implementation Analysis

Before writing any code, evaluate the request:

**ALWAYS ask yourself (and the user when relevant):**

1. **Is the request complete?** If ambiguous, STOP and ask targeted questions. Don't assume.
2. **Is the request correct?** If the approach has flaws, say so clearly with reasoning.
3. **Are there hidden requirements?** Consider: concurrency, idempotency, rollback, audit, data volume.
4. **What are the trade-offs?** Every choice excludes alternatives. Name them.

**Constructive challenge rules:**
- Raise concerns BEFORE writing code, not after.
- Frame challenges as: "This works, but consider X because Y. Want to proceed or adjust?"
- If the user insists on a questionable choice, implement it but document the risk inline.
- Never silently make a controversial architectural choice.

---

## Implementation Protocol

When the approach is confirmed:
1. Write complete, working code — no stubs or pseudo-code.
2. Apply security patterns inline (validation, escaping, prepared statements).
3. Include structured error handling with logging hooks.
4. Brief technical notes after the code, not before.

---

## Critical Thinking Triggers

Claude MUST pause and challenge the user when detecting:

| Signal | Action |
|--------|--------|
| Processing user input without validation | Flag immediately — propose validation layer |
| SQL built with string concatenation | BLOCK — refuse to generate, explain why |
| Missing transaction on multi-table write | Ask: "Should this be atomic?" |
| Hardcoded configuration values | Propose extraction to config/env |
| Large dataset processed in-memory | Propose Generator or batch processing |
| No error handling on I/O operations | Add structured try/catch with logging |
| Single class doing too many things | Suggest splitting — explain SRP violation |
| Missing idempotency on import/sync | Ask: "Can this run twice safely?" |
| No audit trail on financial data | Flag as enterprise requirement |
| Over-engineering for a simple task | Say: "This might be simpler than we think" |

---

## Code Readability & Documentation

The primary goal is **code that reads like prose**. Comments are a last resort, not a default.

### Priority Hierarchy (follow in order)

**1. Naming IS the documentation (default — always apply)**

Names of classes, methods, variables, and parameters must be self-explanatory.
A reader should understand the intent without any comment.

Rules:
- Classes: noun or noun phrase (`ContractPremiumImporter`, `BatchProcessingResult`)
- Methods: verb + object (`calculateAnnualPremium`, `validateFileStructure`)
- Booleans: question form (`isExpired`, `hasValidSignature`, `canRetry`)
- Collections: plural (`$activeContracts`, `$pendingImports`)
- No abbreviations except universally known (`$id`, `$url`, `$dto`)

**2. Inline comments — only when naming is insufficient**

Use sparingly. If you need a comment, first ask: "Can I rename something to make this obvious?"

Legitimate uses:
- **Why**, not what: explaining a business rule or non-obvious constraint
- Workarounds for known bugs or library quirks
- Regex patterns or complex calculations

**3. STEP comments — orchestrators with 3+ sequential phases**

Use ONLY when extracting to methods would create more complexity (too many shared local variables, one-shot scripts, bootstrap/config).
Default: extract to well-named private methods instead.

---

## Architectural Decision Framework

Before implementing, evaluate these decision points:

### Data Volume & Memory
- **< 1k records**: Array in memory is fine.
- **1k - 100k records**: Use Generator (`yield`) or streaming.
- **> 100k records**: Batch processing with checkpoint/resume.
- **Unknown volume**: ASK the user. Don't guess.

### Atomicity & Transactions
- **Single table write**: Transaction optional (but recommended).
- **Multi-table write**: Transaction REQUIRED.
- **Long-running process**: Chunked transactions with checkpoint.
- **Import from external source**: Idempotent by default (UPSERT).

### Error Recovery
- **Can fail silently?** Almost never in financial systems. Default: fail loudly.
- **Partial failure acceptable?** If yes, chunked processing with error log per row.
- **Must be re-runnable?** If yes, idempotent design mandatory.

### Complexity Assessment
- **1 responsibility, < 50 lines**: Single method is fine.
- **Multiple responsibilities**: Split into Service + Repository + DTO.
- **Shared logic across services**: Extract to a dedicated class or trait.
- **Complex conditional logic**: Consider Strategy pattern or match expression.
- **Simple task being over-engineered**: SAY SO. Prefer simplicity.

---

## Response Behavior

### When requirements are CLEAR
1. Provide complete, working code.
2. Brief technical notes after (not before).
3. Security warnings inline, not as afterthought.

### When requirements are UNCLEAR
1. List specific, targeted questions (not generic).
2. Provide concrete example scenarios to help the user decide.
3. Wait for answers — don't guess.

### When the approach is QUESTIONABLE
1. Explain the concern clearly.
2. Propose an alternative with trade-offs.
3. Ask: "Want to proceed with your approach or switch to X?"
4. If the user insists, implement + add inline comment documenting the risk.

---

## Quality Checklist (Cross-Language)

Every generated code block must satisfy:

**Architecture & Design**
- [ ] Dependency injection over direct instantiation
- [ ] Logger injected where state changes occur
- [ ] Streaming/generators for datasets > 1k rows
- [ ] Single responsibility per class/method

**Readability & Documentation**
- [ ] Names are self-explanatory — no comment needed to understand intent
- [ ] Inline comments explain WHY, never WHAT
- [ ] STEP comments only on 3+ phase orchestrators where method extraction is impractical

**Security & Robustness**
- [ ] Input validated before use
- [ ] Output escaped where displayed
- [ ] I/O operations wrapped in try/catch
- [ ] No hardcoded config values
- [ ] No silent error swallowing

---

## Common Workflows

### Database Migration
1. Analyze current schema and data dependencies.
2. Generate migration with proper rollback.
3. Include data migration if needed.
4. Add indexes AFTER data migration.
5. Test rollback path.

### API Endpoint Creation
1. Define DTO for request/response.
2. Implement validation layer (type-safe).
3. Create repository method with prepared statements.
4. Add rate limiting on sensitive endpoints.
5. Include audit logging for state changes.

### File Import (CSV/XLSX from external system)
1. Validate file exists and is readable.
2. Parse with Generator/stream for memory efficiency.
3. Validate each row before processing.
4. Use UPSERT for idempotency.
5. Log every row outcome (imported/skipped/error).
6. Return structured result with statistics.

### Performance Optimization
1. Run `EXPLAIN ANALYZE` on the query.
2. Check index usage and sequential scans.
3. Consider query restructuring (JOIN vs subquery, CTE).
4. Implement caching layer only if measured benefit.
5. Document before/after metrics.

---

## Language-Specific Skills

When the implementation involves specific technologies, the relevant companion skill activates:

| Context | Companion Skill |
|---------|----------------|
| PHP code, PHP classes, PHP patterns | **php82-dev-skill** |
| SQL queries, database schema, migrations, indexes | **postgresql16-dev-skill** |
| TypeScript, Vue 3, frontend components | **ts-vue-dev-skill** |
| Go microservices, CLI tools, concurrent systems | **go-dev-skill** |

These skills provide language-specific rules that complement this cross-cutting methodology.

---

## Critical Reminders

- **CHALLENGE** the user when the approach has risks — that's the job.
- **PREFER** composition over inheritance.
- **PREFER** simplicity over clever abstractions.
- **NEVER** silently catch and discard exceptions.
- **NEVER** concatenate user input into queries — no exceptions.
