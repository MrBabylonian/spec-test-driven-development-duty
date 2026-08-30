---
name: spec-and-test-driven-development-duty
description: Use when implementing a specification or feature list.
version: 0.1.0
metadata:
  package: spec-test-driven-development-duty
  role: entrypoint
---

# Spec & Test-Driven Development Duty

## Overview

Implement requirements as verified vertical slices. Return a behavior-first duty report; assume code is unread.

**REQUIRED PACKAGE SKILL:** Load this package's sibling `test-driven-development`. Preserve its namespace; without a loader, resolve this file's real path and read `../test-driven-development/SKILL.md`.

**REQUIRED PACKAGE REFERENCES:** Before planning or code, read `references/CODE_STYLE.md` and `references/NAMING.md`.

```text
NO IMPLEMENTATION CHANGE BEFORE EXPECTED RED.
NO “COMPLETE” WITHOUT SPEC, INSTRUCTION, AND VERIFICATION EVIDENCE.
```

## Instruction Gate

- Read active system, user, organization, and project instructions through host discovery.
- Follow all referenced files.
- Package standards are mandatory; project rules override only when higher authority permits.
- Turn architecture, code, naming, scope, and verification rules into checks. Ask when precedence remains unclear.

## Spec Ledger

Split every governing spec, feature, and criterion into IDs. Track `source | observable | evidence | status`; never drop prose.

Block an ambiguous external contract unless the user authorizes a provisional assumption. Provisional values stay unapproved, not spec-complete. Label internal assumptions.

## Vertical TDD Loop

For one unblocked ID:

1. Write one behavior test from its criterion.
2. Run it; confirm expected RED from missing behavior.
3. Write minimum compliant code for GREEN.
4. Run the focused test, refactor green, then run affected and required full gates.
5. Re-check the criterion and rules; update the ledger.
6. Repeat.

Never queue all tests first; that is a horizontal slice.

Test inherited code before changing it. A passing characterization test may verify untouched behavior. Never delete inherited code solely because historical RED is unavailable. New or corrected behavior requires RED then GREEN. If this agent wrote the change before RED, revert or delete only that change.

## Completion Gate

Complete only when every requirement has a disposition, changed behavior has RED/GREEN evidence, untouched behavior has direct verification, and every spec, instruction, and tool gate passes.

Fresh unrelated failures may be separated, but block a clean claim. Say `implemented; validation blocked`, not `complete`.

## Duty Report

**REQUIRED TEMPLATE:** Read `templates/duty-report.md` before handoff. Omit code tours, raw logs, and file lists unless needed for impact or action.

## Quick Reference

| Gate | Proof |
|---|---|
| Package | Sibling TDD skill and standards loaded |
| Spec | Every requirement tracked |
| Change | RED → GREEN → refactor |
| Completion | Ledger closed; gates green |

## Rationalizations

| Excuse | Reality |
|---|---|
| “Correct first; test later.” | Correction before RED is tests-after. |
| “Make a provisional guess.” | It stays provisional. |
| “All tests first enables parallelism.” | It loses per-slice feedback. |
| “Tests pass; spec done.” | Tests can omit prose. |
| “Failures are old; approved.” | Neither is fresh evidence. |
| “Naming compliance causes churn.” | Naming is an acceptance check. |
| “Inherited code lacks RED; delete it.” | Preserve it; RED governs new changes. |

## Red Flags — Stop

- Package dependency unread
- Change before RED
- Deleting inherited code to recreate RED
- Several RED tests before GREEN
- Guessed or untracked requirement
- Required reference unread
- `Complete` with a blocker or failed gate

## Common Mistakes

- Untestable title: derive an observable or block it.
- Report outcomes and risks—not internals.
