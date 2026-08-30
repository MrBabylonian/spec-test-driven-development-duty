---
name: spec-and-test-driven-development-duty
description: Use when implementing a specification or feature list.
version: 0.3.0
metadata:
  package: spec-test-driven-development-duty
  role: entrypoint
---

# Spec & Test-Driven Development Duty

## Overview

Route clarified specifications through planned TDD implementation, per-task reviews, simplification, final review, and duty reporting.

**PACKAGE SKILLS:** Load this package's `subagent-driven-development`, `test-driven-development`, `simplify-code`, and `requesting-code-review` in one namespace. Without a loader, resolve this file's real path and read sibling skill directories.

**PACKAGE STANDARDS:** Read `references/CODE_STYLE.md` and `references/NAMING.md`.

```text
NO IMPLEMENTATION WITHOUT PROVIDED, UNAMBIGUOUS REQUIREMENTS AND EXPECTED RED.
NO COMPLETION BEFORE ROUTED IMPLEMENTATION, SIMPLIFICATION, FINAL REVIEW, AND EVERY GATE.
```

## Instruction Gate — Every Role

Before every stage and delegated task or review, re-read applicable `AGENTS.md`, every file it references, and both standards. Every delegated implementer and reviewer receives current rules or accessible exact paths and confirms compliance. Changed rules require revalidation; unavailable rules block. No exception exists for deadlines, approval, convenience, or passing tests.

## Input Gate

If neither specifications nor features are provided, ask the user to provide them, then **STOP**. Never inspect, test, design, or infer scope.

Convert supplied requirements into IDs with observable acceptance. If any ambiguity remains, ask all clarification questions together, then **STOP**. Only the engineer's answers close ambiguity; until then do not infer, test, or implement.

## Mandatory Routing

1. **Input:** Pass Input and Instruction gates.
2. **Plan:** Create ordered task cards from the ledger; classify task independence and file overlap. Load `subagent-driven-development` to apply its routing and review discipline.
3. **Independent implementation:** With isolated agents, use `subagent-driven-development`: one fresh implementer per task with packaged TDD, then spec-compliance review and code-quality review. Fix and re-review before the next task.
4. **Coupled implementation:** For overlapping tasks, use controller-run vertical TDD; retain fresh spec and quality reviewers. **No isolated reviewer capability:** block.
5. **Simplification:** After task/integration gates pass, execute `simplify-code`; rerun tests and spec checks. Per-task reviews do not replace it.
6. **Final review:** Execute `requesting-code-review` with spec, ledger, diff, and evidence. Task reviews do not replace it.
7. **Remediation:** Fix Critical or Important findings; behavior changes require RED→GREEN. Repeat Simplification and Final review until clear.
8. **Handoff:** Re-run the Instruction gate, close the ledger, and use `templates/duty-report.md`.

Never reorder, combine, waive, or skip stages. Git side effects require separate user authorization.

## Completion Gate

Complete only with resolved requirements, evidenced ledger, recorded role gates, approved per-task reviews, passing simplification, blocker-free final review, and green required tests. Otherwise report `blocked` or `partial`.

## Quick Reference

| Route | Required behavior |
|---|---|
| Independent | Fresh implementer + two reviews |
| Coupled | Controller TDD + fresh reviewers |
| Final | Simplify, then review |

## Rationalizations

| Excuse | Reality |
|---|---|
| “Delegate everything.” | Classify overlap first. |
| “Per-task approval is enough.” | Final cleanup/review still run. |
| “Rules were read earlier.” | Refresh for every role. |

## Red Flags — Stop

- Missing or ambiguous requirement
- Unread instruction reference
- Reviewer context missing current rules
- Stage skipped, reordered, or blocked

## Common Mistakes

- Treating green implementation or per-task approval as workflow completion.
