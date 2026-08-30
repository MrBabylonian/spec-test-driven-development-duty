# Spec & Test-Driven Development Duty

A self-contained, versioned methodology package for implementing specifications through vertical test-driven development. It keeps the entrypoint skill, TDD discipline, coding standard, naming standard, report contract, manifests, validation, and tests in one repository revision.

## Package contents

```text
plugin.json                                      Agent Plugins v1 manifest
COMPONENTS.json                                  Component versions and digests
skills/
  spec-and-test-driven-development-duty/
    SKILL.md                                     Portable entrypoint
    references/CODE_STYLE.md                     Mandatory coding standard
    references/NAMING.md                         Mandatory naming standard
    templates/duty-report.md                     Seven-field handoff contract
  test-driven-development/
    SKILL.md                                     Portable wrapper for selected TDD
  simplify-code/
    SKILL.md                                     Portable simplification wrapper
  requesting-code-review/
    SKILL.md                                     Portable review wrapper
  subagent-driven-development/
    SKILL.md                                     Portable orchestration wrapper
vendor/
  test-driven-development/
    SKILL.md                                     Verbatim selected TDD skill v1.1.0
  simplify-code/
    SKILL.md                                     Verbatim simplify-code v1.1.0
  requesting-code-review/
    SKILL.md                                     Verbatim requesting-code-review
    code-reviewer.md                             Reviewer prompt template
  subagent-driven-development/
    SKILL.md                                     Verbatim orchestration skill v1.1.0
    references/                                  Gate and context disciplines
.claude-plugin/                                  Claude Code manifests
.codex-plugin/                                   Codex plugin manifest
.agents/plugins/                                 Codex-compatible marketplace
scripts/validate_package.py                      Dependency-free validator
tests/test_package.py                            Package contract tests
```

## Entry point

Load `spec-and-test-driven-development-duty`. It requires the sibling orchestration, TDD, simplification, and review wrappers plus both packaged standards. Each wrapper loads its exact vendored source. The entrypoint and wrappers contain no host-specific runtime paths or commands.

The mandatory workflow is: obtain complete specifications/features → clarify every ambiguity → classify task independence and overlap → route independent tasks through `subagent-driven-development` with per-task TDD and two-stage review, or tightly coupled tasks through controller-run TDD with fresh reviewers → run `simplify-code` → run final `requesting-code-review` → remediate and repeat cleanup/review until clear → issue the duty report. Applicable `AGENTS.md` files and every referenced file are refreshed for every stage and delegated role.

## Methodology boundary

The package owns every methodology dependency: duty workflow, TDD discipline, code style, naming, anti-pattern guidance, and report contract. Active host and project inputs—such as repository instructions, build commands, and application tests—remain external because they describe the project being changed, not this methodology.

Version 0.3.0 does not auto-run or enforce policy through hooks. The host must load or invoke the entrypoint skill. Its verification gates then fail closed when required project evidence is unavailable.

## Installation

### Agent Plugins v1 hosts

Install or clone the repository with the host's plugin manager. The root `plugin.json` exposes every `skills/*/SKILL.md` directory.

### Hermes Agent

Install a published repository with:

```bash
hermes plugins install <owner>/<repository> --enable
```

For local development, place the checkout directly under the active profile's `plugins/` directory, enable `spec-test-driven-development-duty`, then start a fresh session.

### Claude Code

Add this checkout as a local marketplace, then install `spec-test-driven-development-duty@spec-test-driven-development-duty-dev` through the plugin UI.

### Codex-compatible hosts

Use `.codex-plugin/plugin.json` or `.agents/plugins/marketplace.json` through the host's plugin manager. If plugin installation is unavailable, copy both directories under `skills/` into the host's Agent Skills directory.

## Versioning

`VERSION`, plugin manifests, the entrypoint, and portable wrappers carry package version `0.3.0`. Vendored sources retain their source versions when declared. `COMPONENTS.json` records wrapper-to-source relations, source identities, versions, companion files, copy mode, and digests. Change governed artifacts in one commit and release one tag. Roll back the package revision, not individual files.

## Validation

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

Both commands use only the Python standard library.

## Local source-of-truth wiring

A host may link existing global standards or standalone skill locations to this checkout. Those links are installation adapters, not package content. The package itself contains no symbolic links and remains portable.

## Public distribution

Read `NOTICE.md` before publishing. Add an explicit license and repository URLs only after the owner chooses the public destination and license.
