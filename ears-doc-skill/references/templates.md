# EARS Document Templates

Ready-to-use templates for EARS-based specification documents.
Adapt section headings to project needs; do not remove required fields.

---

## Template 1: Full Software Requirements Specification (SRS)

```markdown
# Software Requirements Specification
## <System Name>

| Field        | Value                   |
|--------------|-------------------------|
| Version      | 1.0.0                   |
| Status       | [DRAFT] / [APPROVED]    |
| Date         | YYYY-MM-DD              |
| Author       | <Name>                  |
| Reviewed by  | <Name>                  |

---

## 1. Purpose and Scope

<One paragraph: what system is being specified, what it is NOT specifying,
and who the intended audience is.>

---

## 2. Definitions and Glossary

| Term | Definition |
|------|------------|
| <Term> | <Precise definition used throughout this document> |

---

## 3. System Overview

<System context diagram or textual description of system boundaries,
external actors, and primary interfaces.>

**System Name (used in requirements):** `<ExactSystemName>`

**External Actors:**
- <Actor 1>: <role>
- <Actor 2>: <role>

---

## 4. Assumptions and Constraints

- <ASM-001>: <assumption>
- <CON-001>: <constraint>

---

## 5. Requirements

### 5.1 <Domain Name> (e.g., Authentication)

#### REQ-<DOM>-001: <Short Title>

| Field      | Value                        |
|------------|------------------------------|
| Pattern    | <EARS Pattern>               |
| Priority   | Must / Should / Could / Won't|
| Status     | [DRAFT]                      |
| Source     | <Story/Regulation/Goal ID>   |

**Statement:**
<EARS-formatted requirement>

**Rationale:**
<One sentence explaining why this behavior is required.>

**Acceptance Criteria:**
- [ ] Given <context>, when <action>, then <expected outcome>
- [ ] <Additional testable condition>

---

#### REQ-<DOM>-002: <Short Title>

...

### 5.2 <Next Domain>

...

---

## 6. Non-Functional Requirements

### 6.1 Performance

| REQ-NFR-PERF-001 | Response Time |
| Pattern | Ubiquitous |
| Priority | Must |
| Status | [DRAFT] |

**Statement:**
The <system name> shall respond to <operation type> requests within
<N> milliseconds at the 99th percentile under a load of <N> concurrent users.

### 6.2 Security

...

### 6.3 Availability

...

### 6.4 Scalability

...

---

## 7. Open Issues

| ID | Description | Owner | Due |
|----|-------------|-------|-----|
| OI-001 | <Unresolved question> | <Name> | YYYY-MM-DD |

---

## 8. Traceability Matrix

| Requirement ID | Source | Implements | Tested by |
|----------------|--------|------------|-----------|
| REQ-AUTH-001 | US-042 | — | TC-AUTH-001 |

---

## 9. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | <Name> | Initial draft |
```

---

## Template 2: Feature Specification (lightweight)

For single-feature specs within an existing product.

```markdown
# Feature Specification: <Feature Name>

| Field      | Value                  |
|------------|------------------------|
| Feature ID | FEAT-<NNN>             |
| Version    | 1.0.0                  |
| Status     | [DRAFT]                |
| Date       | YYYY-MM-DD             |

## Problem Statement

<Two sentences: what user need or business problem does this feature address?>

## Out of Scope

- <Explicitly excluded behavior 1>
- <Explicitly excluded behavior 2>

## Glossary

| Term | Definition |
|------|------------|

## Requirements

### Functional

#### REQ-<FEAT>-001: <Title>
...

### Non-Functional

#### REQ-<FEAT>-NFR-001: <Title>
...

## Acceptance Criteria (Feature-Level)

- [ ] <End-to-end testable scenario 1>
- [ ] <End-to-end testable scenario 2>

## Open Questions

- [ ] <Question requiring stakeholder input>
```

---

## Template 3: Requirements Review Report

For reviewing an existing requirements document.

```markdown
# Requirements Review Report
## <Document Name>

| Field      | Value          |
|------------|----------------|
| Reviewer   | <Name>         |
| Date       | YYYY-MM-DD     |
| Document   | <Title + Ver>  |

## Summary

- **Requirements reviewed:** N
- **Defects found:** N
- **Requirements requiring rewrite:** N
- **Open coverage gaps:** N

## Defect Report

| Req ID | Defect Type | Description | Severity | Suggested Fix |
|--------|-------------|-------------|----------|---------------|
| REQ-001 | Ambiguity | "it" refers to unclear actor | High | Replace "it" with system name |
| REQ-004 | Vagueness | "quickly" has no measurable bound | High | Add "within 200ms at p99" |
| REQ-007 | Complexity | Two distinct behaviors in one statement | Medium | Split into REQ-007a, REQ-007b |

## Severity Definitions

| Severity | Meaning |
|----------|---------|
| Critical | Requirement is untestable or contradicts another |
| High | Requirement is ambiguous or vague |
| Medium | Requirement is complex or wordy |
| Low | Minor style or consistency issue |

## Rewritten Requirements

### REQ-<NNN> (original → corrected)

**Original:**
> <original text>

**Defect:** <type and explanation>

**Corrected:**
> <EARS-formatted replacement>

## Coverage Gaps

Behaviors identified as missing from the current requirement set:

1. <Gap description> — suggested pattern: <EARS pattern>
2. <Gap description> — suggested pattern: <EARS pattern>
```

---

## Template 4: Single Requirement Block (copy-paste unit)

```markdown
### REQ-<DOMAIN>-<NNN>: <Short Imperative Title>

| Field      | Value                        |
|------------|------------------------------|
| Pattern    | <Ubiquitous / State-Driven / Event-Driven / Optional Feature / Unwanted Behavior / Complex> |
| Priority   | Must / Should / Could / Won't|
| Status     | [DRAFT] / [APPROVED]        |
| Source     | <User story / regulation / goal ID> |

**Statement:**
[While <precondition>,] [when/if <trigger>,] [then] the <system name> shall <system response>.

**Rationale:**
<One sentence: why this behavior is required.>

**Acceptance Criteria:**
- [ ] Given <context>, when <action or state>, then <expected observable outcome>
- [ ] <Additional testable condition>

**Notes:**
<Optional: implementation hints, references to related requirements, known edge cases>
```

---

## Naming Conventions

### Requirement ID Format

```
REQ-<DOMAIN>-<NNN>

Examples:
  REQ-AUTH-001   Authentication domain, first requirement
  REQ-PAY-012    Payment domain, twelfth requirement
  REQ-NFR-SEC-001  Non-functional, security subdomain
```

### Domain Codes (suggested)

| Code | Domain |
|------|--------|
| AUTH | Authentication & Authorization |
| DAT | Data management & persistence |
| UI | User interface |
| API | External API / integration |
| NFR | Non-functional requirements |
| SEC | Security |
| PERF | Performance |
| AVAIL | Availability & reliability |
| AUDIT | Audit & logging |
| NOTIF | Notifications |
| ADMIN | Administration |

### Priority (MoSCoW)

| Label | Meaning |
|-------|---------|
| Must | Non-negotiable; system fails without this |
| Should | High value; include unless strong reason not to |
| Could | Nice to have; include if capacity allows |
| Won't | Explicitly excluded from this release |
