from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


AGENT_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PACKAGE_NAME = "spec-test-driven-development-duty"


class PackageValidationError(RuntimeError):
    """Raised when the package violates its distribution contract."""


class FrontmatterReader:
    @staticmethod
    def read(document_path: Path) -> dict[str, str]:
        document_text = document_path.read_text(encoding="utf-8")
        if not document_text.startswith("---\n"):
            raise PackageValidationError(f"Missing frontmatter: {document_path}")
        sections = document_text[4:].split("\n---\n", 1)
        if len(sections) != 2:
            raise PackageValidationError(f"Unterminated frontmatter: {document_path}")
        parsed_fields: dict[str, str] = {}
        for source_line in sections[0].splitlines():
            match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.+)$", source_line)
            if match:
                parsed_fields[match.group(1)] = match.group(2).strip()
        return parsed_fields


class PackageValidator:
    def __init__(self, package_root: Path) -> None:
        self.package_root = package_root.resolve()
        self.package_version = (
            self.package_root / "VERSION"
        ).read_text(encoding="utf-8").strip()
        self.errors: list[str] = []

    def validate(self) -> None:
        self._validate_version()
        self._validate_paths()
        self._validate_manifests()
        self._validate_components()
        self._validate_skills()
        self._validate_portability()
        self._validate_report()
        self._validate_symlinks()
        if self.errors:
            joined_errors = "\n".join(f"- {message}" for message in self.errors)
            raise PackageValidationError(f"Package validation failed:\n{joined_errors}")

    def _validate_version(self) -> None:
        if re.fullmatch(r"\d+\.\d+\.\d+", self.package_version) is None:
            self.errors.append(f"Invalid VERSION: {self.package_version!r}")

    def _validate_paths(self) -> None:
        required_paths = (
            "plugin.json",
            "COMPONENTS.json",
            "README.md",
            "NOTICE.md",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".codex-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            ".cursor-plugin/marketplace.json",
            ".agents/plugins/marketplace.json",
            "skills/spec-and-test-driven-development-duty/SKILL.md",
            "skills/spec-and-test-driven-development-duty/references/CODE_STYLE.md",
            "skills/spec-and-test-driven-development-duty/references/NAMING.md",
            "skills/spec-and-test-driven-development-duty/templates/duty-report.md",
            "skills/subagent-driven-development/SKILL.md",
            "skills/test-driven-development/SKILL.md",
            "vendor/subagent-driven-development/SKILL.md",
            "vendor/subagent-driven-development/references/context-budget-discipline.md",
            "vendor/subagent-driven-development/references/gates-taxonomy.md",
            "vendor/test-driven-development/SKILL.md",
            "tests/test_package.py",
        )
        for relative_path in required_paths:
            if not (self.package_root / relative_path).is_file():
                self.errors.append(f"Missing required file: {relative_path}")

    def _read_json(self, relative_path: str) -> dict:
        manifest_path = self.package_root / relative_path
        try:
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.errors.append(f"Invalid JSON {relative_path}: {error}")
            return {}
        if not isinstance(manifest_payload, dict):
            self.errors.append(f"Manifest is not an object: {relative_path}")
            return {}
        return manifest_payload

    def _validate_manifests(self) -> None:
        portable_manifest = self._read_json("plugin.json")
        if portable_manifest.get("$schema") != AGENT_PLUGIN_SCHEMA:
            self.errors.append("plugin.json has the wrong Agent Plugins schema")
        if portable_manifest.get("name") != PACKAGE_NAME:
            self.errors.append("plugin.json has the wrong package name")

        versioned_manifests = (
            "plugin.json",
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
        )
        for relative_path in versioned_manifests:
            manifest_payload = self._read_json(relative_path)
            if manifest_payload.get("version") != self.package_version:
                self.errors.append(f"Version mismatch: {relative_path}")

        marketplace_payload = self._read_json(".claude-plugin/marketplace.json")
        marketplace_plugins = marketplace_payload.get("plugins")
        if not isinstance(marketplace_plugins, list) or len(marketplace_plugins) != 1:
            self.errors.append("Claude marketplace must declare exactly one plugin")
        elif marketplace_plugins[0].get("version") != self.package_version:
            self.errors.append("Claude marketplace version mismatch")

        agents_marketplace = self._read_json(".agents/plugins/marketplace.json")
        agents_plugins = agents_marketplace.get("plugins")
        if not isinstance(agents_plugins, list) or len(agents_plugins) != 1:
            self.errors.append("Agent marketplace must declare exactly one plugin")

    def _validate_skills(self) -> None:
        skills_root = self.package_root / "skills"
        components_payload = self._read_json("COMPONENTS.json")
        component_contracts = components_payload.get("components") or {}
        discovered_skill_paths = sorted(skills_root.glob("*/SKILL.md"))
        expected_names = {
            "requesting-code-review",
            "simplify-code",
            "spec-and-test-driven-development-duty",
            "subagent-driven-development",
            "test-driven-development",
        }
        discovered_names = {skill_path.parent.name for skill_path in discovered_skill_paths}
        if discovered_names != expected_names:
            self.errors.append(f"Unexpected skill set: {sorted(discovered_names)}")

        for skill_path in discovered_skill_paths:
            frontmatter_fields = FrontmatterReader.read(skill_path)
            if frontmatter_fields.get("name") != skill_path.parent.name:
                self.errors.append(f"Skill name mismatch: {skill_path}")
            component_contract = component_contracts.get(skill_path.parent.name) or {}
            expected_version = component_contract.get("version")
            if frontmatter_fields.get("version") != expected_version:
                self.errors.append(f"Skill version mismatch: {skill_path}")
            description = frontmatter_fields.get("description", "")
            if not description or len(description) > 1024:
                self.errors.append(f"Invalid skill description: {skill_path}")

        entrypoint_path = (
            skills_root / "spec-and-test-driven-development-duty" / "SKILL.md"
        )
        entrypoint_text = entrypoint_path.read_text(encoding="utf-8")
        entrypoint_words = re.findall(r"\b[\w’'-]+\b", entrypoint_text)
        if len(entrypoint_words) >= 500:
            self.errors.append(
                f"Entrypoint exceeds word budget: {len(entrypoint_words)} words"
            )

    def _validate_components(self) -> None:
        components_payload = self._read_json("COMPONENTS.json")
        if components_payload.get("package_version") != self.package_version:
            self.errors.append("COMPONENTS.json package version mismatch")
        component_contracts = components_payload.get("components")
        if not isinstance(component_contracts, dict):
            self.errors.append("COMPONENTS.json components must be an object")
            return

        vendored_contracts = (
            (
                "test-driven-development",
                "test-driven-development-source",
                ["SKILL.md"],
            ),
            ("simplify-code", "simplify-code-source", ["SKILL.md"]),
            (
                "subagent-driven-development",
                "subagent-driven-development-source",
                [
                    "SKILL.md",
                    "references/context-budget-discipline.md",
                    "references/gates-taxonomy.md",
                ],
            ),
            (
                "requesting-code-review",
                "requesting-code-review-source",
                ["SKILL.md", "agents/openai.yaml", "code-reviewer.md"],
            ),
        )
        for wrapper_name, source_name, expected_files in vendored_contracts:
            self._validate_vendored_skill(
                component_contracts,
                wrapper_name,
                source_name,
                expected_files,
            )

    def _validate_vendored_skill(
        self,
        component_contracts: dict,
        wrapper_name: str,
        source_name: str,
        expected_files: list[str],
    ) -> None:
        wrapper_contract = component_contracts.get(wrapper_name)
        if not isinstance(wrapper_contract, dict):
            self.errors.append(f"Missing portable wrapper contract: {wrapper_name}")
            return
        source_component_name = wrapper_contract.get("source_component")
        if source_component_name != source_name:
            self.errors.append(f"Wrong source component for wrapper: {wrapper_name}")

        source_contract = component_contracts.get(source_component_name)
        if not isinstance(source_contract, dict):
            self.errors.append(f"Missing vendored component contract: {source_name}")
            return
        if source_contract.get("copy_mode") != "verbatim":
            self.errors.append(f"Vendored component is not verbatim: {source_name}")
        source_relative_path = source_contract.get("path")
        if not isinstance(source_relative_path, str):
            self.errors.append(f"Vendored component path is invalid: {source_name}")
            return
        source_path = self.package_root / source_relative_path
        if not source_path.is_file():
            self.errors.append(f"Vendored component file is missing: {source_name}")
            return
        actual_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_digest != source_contract.get("sha256"):
            self.errors.append(f"Vendored component digest mismatch: {source_name}")

        source_directory_files = sorted(
            package_path.relative_to(source_path.parent).as_posix()
            for package_path in source_path.parent.rglob("*")
            if package_path.is_file()
        )
        if source_directory_files != expected_files:
            self.errors.append(
                f"Unexpected files in {source_name}: {source_directory_files}"
            )

        companion_contracts = source_contract.get("companion_files") or {}
        if not isinstance(companion_contracts, dict):
            self.errors.append(f"Invalid companion files: {source_name}")
        else:
            for companion_path_text, expected_digest in companion_contracts.items():
                companion_path = self.package_root / companion_path_text
                if not companion_path.is_file():
                    self.errors.append(f"Missing companion file: {companion_path_text}")
                    continue
                companion_digest = hashlib.sha256(companion_path.read_bytes()).hexdigest()
                if companion_digest != expected_digest:
                    self.errors.append(f"Companion digest mismatch: {companion_path_text}")

        wrapper_path = self.package_root / str(wrapper_contract.get("path", ""))
        if not wrapper_path.is_file():
            self.errors.append(f"Portable wrapper file is missing: {wrapper_name}")
            return
        wrapper_text = wrapper_path.read_text(encoding="utf-8")
        vendor_directory = source_name.removesuffix("-source")
        required_path = f"../../vendor/{vendor_directory}/SKILL.md"
        if required_path not in wrapper_text:
            self.errors.append(f"Portable wrapper misses vendored source: {wrapper_name}")

    def _validate_portability(self) -> None:
        entrypoint_path = (
            self.package_root
            / "skills/spec-and-test-driven-development-duty/SKILL.md"
        )
        entrypoint_text = entrypoint_path.read_text(encoding="utf-8")
        forbidden_fragments = (
            "~/.hermes",
            ".resolved.md",
            "skill_view(",
            "hermes ",
            "software-development/test-driven-development",
            "verification-before-completion",
        )
        for forbidden_fragment in forbidden_fragments:
            if forbidden_fragment in entrypoint_text:
                self.errors.append(
                    f"Host-specific entrypoint fragment: {forbidden_fragment}"
                )

        required_fragments = (
            "subagent-driven-development",
            "test-driven-development",
            "simplify-code",
            "requesting-code-review",
            "resolve this file's real path",
            "references/CODE_STYLE.md",
            "references/NAMING.md",
            "templates/duty-report.md",
        )
        for required_fragment in required_fragments:
            if required_fragment not in entrypoint_text:
                self.errors.append(f"Missing package reference: {required_fragment}")

    def _validate_report(self) -> None:
        template_path = (
            self.package_root
            / "skills/spec-and-test-driven-development-duty/templates/duty-report.md"
        )
        template_text = template_path.read_text(encoding="utf-8")
        required_fields = (
            "**Status:**",
            "**Delivered:**",
            "**Coverage:**",
            "**Verification:**",
            "**Decisions:**",
            "**Risks or deviations:**",
            "**Engineer action:**",
        )
        for required_field in required_fields:
            if template_text.count(required_field) != 1:
                self.errors.append(f"Duty field count mismatch: {required_field}")
        if "Return only these seven fields." not in template_text:
            self.errors.append("Duty template lacks the seven-field output rule")

    def _validate_symlinks(self) -> None:
        for package_path in self.package_root.rglob("*"):
            if package_path.is_symlink():
                relative_path = package_path.relative_to(self.package_root)
                self.errors.append(f"Package contains a symbolic link: {relative_path}")


def main() -> int:
    package_root = Path(__file__).resolve().parents[1]
    validator = PackageValidator(package_root)
    try:
        validator.validate()
    except PackageValidationError as error:
        print(error, file=sys.stderr)
        return 1
    print(
        "Package validation passed: "
        f"{PACKAGE_NAME} {validator.package_version}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
