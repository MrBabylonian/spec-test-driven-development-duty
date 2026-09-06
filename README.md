# Spec & Test-Driven Development Duty

A self-contained Agent Skill for implementing specifications through vertical test-driven development, independent review, simplification, and final verification.

## Skill contents

```text
SKILL.md                                      Skill entrypoint
references/
  CODE_STYLE.md                               Mandatory coding standard
  NAMING.md                                   Mandatory naming standard
  test-driven-development.md                  Test-first workflow
  subagent-driven-development.md              Task routing and review workflow
  simplify-code.md                            Simplification workflow
  requesting-code-review.md                   Final review workflow
  code-reviewer.md                            Reviewer prompt template
  context-budget-discipline.md                Context management rules
  gates-taxonomy.md                           Validation gate definitions
templates/
  duty-report.md                              Seven-field handoff contract
COMPONENTS.json                               Component versions and provenance
NOTICE.md                                     Source and distribution notice
VERSION                                       Skill version
scripts/validate_package.py                   Dependency-free validator
tests/test_package.py                         Package contract tests
```

## Installation

Copy or clone this repository as one folder inside the host's personal skills directory. The resulting path must place `SKILL.md` directly inside the folder named `spec-test-driven-development-duty`.

### Cursor

```text
~/.cursor/skills/spec-test-driven-development-duty/SKILL.md
```

On Windows:

```text
C:\Users\<username>\.cursor\skills\spec-test-driven-development-duty\SKILL.md
```

### Claude Code

```text
~/.claude/skills/spec-test-driven-development-duty/SKILL.md
```

### Codex

```text
~/.codex/skills/spec-test-driven-development-duty/SKILL.md
```

Start a new agent session after copying the folder. No plugin installation, marketplace registration, symbolic link, or local-plugin permission is required.

## Entry point

Invoke `spec-test-driven-development-duty`. The entrypoint reads the packaged standards and loads each supporting workflow from `references/` when its stage begins.

The mandatory workflow is: obtain complete specifications or features → clarify every ambiguity → classify task independence and overlap → route implementation through test-driven development and two-stage review → simplify the result → run final review → remediate and repeat until clear → issue the duty report.

## Methodology boundary

The skill owns every methodology dependency: duty workflow, test-driven development discipline, code style, naming, anti-pattern guidance, and report contract. Active host and project inputs—such as repository instructions, build commands, and application tests—remain external because they describe the project being changed.

Version 0.3.0 does not auto-run or enforce policy through hooks. The host must load or invoke `SKILL.md`. Its verification gates fail closed when required project evidence is unavailable.

## Validation

```bash
python scripts/validate_package.py
python -m unittest discover -s tests -v
```

Both commands use only the Python standard library.

## Public distribution

Read `NOTICE.md` before publishing. Add an explicit license only after the owner chooses one.
