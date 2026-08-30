---
name: spec-and-test-driven-development-duty
description: Use when implementing a specification or feature list.
version: 0.2.0
metadata:
  package: spec-test-driven-development-duty
  role: entrypoint
---

# Spec & Test-Driven Development Duty

## Overview

Run specifications through TDD, simplification, review, and duty reporting.

**PACKAGE SKILLS:** Use this package's `test-driven-development`, then `simplify-code`, then `requesting-code-review`. Preserve package namespace. Without a loader, resolve this file's real path and read `../test-driven-development/SKILL.md`, `../simplify-code/SKILL.md`, and `../requesting-code-review/SKILL.md`.

**PACKAGE STANDARDS:** Using that real-path base, read `references/CODE_STYLE.md` and `references/NAMING.md`.

```text
NO IMPLEMENTATION WITHOUT PROVIDED, UNAMBIGUOUS REQUIREMENTS AND EXPECTED RED.
NO COMPLETION BEFORE SIMPLIFICATION, INDEPENDENT REVIEW, AND EVERY STAGE GATE.
```

## Instruction Gate — Every Stage

Before every stage—Input, Implementation, Simplification, Review, Remediation, and Handoff—rediscover and re-read applicable `AGENTS.md` plus every file it references, then re-read both package standards. Never rely on an earlier read. If a rule changed, revalidate affected work. If any required file is unavailable, block. No exception exists for deadlines, approval, convenience, or prior passing tests.

## Input Gate

If neither specifications nor features are provided, ask the user to provide them, then **STOP**. Do not inspect, test, design, or implement guessed scope.

When requirements are provided, split them into IDs with source, observable acceptance, evidence, and status. If any ambiguity remains, ask all clarification questions in one batch, then **STOP**. Only the engineer's answers close ambiguity; until then do not infer, test, or implement.

## Mandatory Sequence

1. **Input:** Pass the Input and Instruction gates.
2. **Implementation:** Load `test-driven-development`. For one requirement at a time: test → expected RED → minimum compliant GREEN → refactor → focused and required full gates. Update the ledger. Never queue all tests first.
3. **Simplification:** Only after every requirement is implemented and green, load and execute `simplify-code`. Re-run affected/full gates and re-check the complete specification. Route any discovered behavior defect through a new TDD cycle.
4. **Review:** Only after simplification passes, load and execute `requesting-code-review` with the specification, ledger, diff, and evidence.
5. **Remediation:** Fix every Critical or Important finding before proceeding. Behavior changes require RED→GREEN. Then repeat Simplification and Review until no blocking finding remains.
6. **Handoff:** Re-run the Instruction gate, close the ledger, and use `templates/duty-report.md`.

Never reorder, combine, waive, or skip stages.

## Completion Gate

Complete only when requirements and ambiguities are resolved, every ledger item is evidenced, all stage instruction checks are recorded, simplification passed, independent review has no blocking finding, and required tests and gates are green. Otherwise report `blocked` or `partial`.

## Quick Reference

| Stage | Exit proof |
|---|---|
| Input | Complete, unambiguous requirements |
| Implementation | Per-item RED→GREEN evidence |
| Simplification | Cleanup verified against tests/spec |
| Review | No Critical or Important finding |
| Handoff | Closed ledger and duty report |

## Rationalizations

| Excuse | Reality |
|---|---|
| “Infer the missing scope.” | Ask, then stop. |
| “A lead authorized assumptions.” | Only engineer answers close ambiguity. |
| “Tests pass; finish now.” | Simplify, then review. |
| “Rules were read earlier.” | Re-read them at every stage. |

## Red Flags — Stop

- Missing or ambiguous requirement
- Unread `AGENTS.md` reference
- Stage skipped or reordered
- Review blocker unresolved

## Common Mistakes

- Treating implementation-green as workflow-complete.
