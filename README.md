# Spec & Test-Driven Development Duty

A self-contained, versioned methodology package for implementing specifications through vertical test-driven development. It keeps the entrypoint skill, TDD discipline, coding standard, naming standard, report contract, manifests, validation, and tests in one repository revision.

## Package contents

```text
plugin.json                                      Agent Plugins v1 manifest
skills/
  spec-and-test-driven-development-duty/
    SKILL.md                                     Portable entrypoint
    references/CODE_STYLE.md                     Mandatory coding standard
    references/NAMING.md                         Mandatory naming standard
    templates/duty-report.md                     Seven-field handoff contract
  test-driven-development/
    SKILL.md                                     Packaged TDD discipline
    testing-anti-patterns.md                     Supporting TDD reference
.claude-plugin/                                  Claude Code manifests
.codex-plugin/                                   Codex plugin manifest
.agents/plugins/                                 Codex-compatible marketplace
scripts/validate_package.py                      Dependency-free validator
tests/test_package.py                            Package contract tests
```

## Entry point

Load `spec-and-test-driven-development-duty`. It requires the sibling `test-driven-development` skill and the two packaged standards. The skills contain no host-specific runtime paths or commands.

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

`VERSION`, every plugin manifest, and both skill frontmatters carry the same semantic version. Change all governed artifacts in one commit and release one tag. Roll back the package revision, not individual files.

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
