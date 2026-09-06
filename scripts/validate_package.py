from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


SKILL_NAME = "spec-test-driven-development-duty"
SUPPORTING_COMPONENT_NAMES = frozenset(
    {
        "requesting-code-review",
        "simplify-code",
        "subagent-driven-development",
        "test-driven-development",
    }
)
EXPECTED_COMPONENT_NAMES = SUPPORTING_COMPONENT_NAMES | {SKILL_NAME}
DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}")


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
        self._validate_components()
        self._validate_skill()
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
            "SKILL.md",
            "COMPONENTS.json",
            "README.md",
            "NOTICE.md",
            "VERSION",
            "references/CODE_STYLE.md",
            "references/NAMING.md",
            "references/code-reviewer.md",
            "references/context-budget-discipline.md",
            "references/gates-taxonomy.md",
            "references/requesting-code-review.md",
            "references/simplify-code.md",
            "references/subagent-driven-development.md",
            "references/test-driven-development.md",
            "templates/duty-report.md",
            "tests/test_package.py",
        )
        for relative_path in required_paths:
            if not (self.package_root / relative_path).is_file():
                self.errors.append(f"Missing required file: {relative_path}")

        forbidden_paths = (
            "plugin.json",
            ".agents",
            ".claude-plugin",
            ".codex-plugin",
            ".cursor-plugin",
            "skills",
            "vendor",
        )
        for relative_path in forbidden_paths:
            if (self.package_root / relative_path).exists():
                self.errors.append(f"Plugin packaging path remains: {relative_path}")

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

    def _validate_skill(self) -> None:
        skill_path = self.package_root / "SKILL.md"
        frontmatter_fields = FrontmatterReader.read(skill_path)
        if frontmatter_fields.get("name") != SKILL_NAME:
            self.errors.append("SKILL.md has the wrong skill name")
        if frontmatter_fields.get("version") != self.package_version:
            self.errors.append("SKILL.md version does not match VERSION")
        description = frontmatter_fields.get("description", "")
        if not description or len(description) > 1024:
            self.errors.append("SKILL.md has an invalid description")

        entrypoint_text = skill_path.read_text(encoding="utf-8")
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

        self._validate_component_names(component_contracts)
        entrypoint_contract = component_contracts.get(SKILL_NAME)
        if not isinstance(entrypoint_contract, dict):
            self.errors.append(f"Missing entrypoint component: {SKILL_NAME}")
        elif entrypoint_contract.get("path") != "SKILL.md":
            self.errors.append("Entrypoint component has the wrong path")

        for component_name, component_contract in component_contracts.items():
            if not isinstance(component_contract, dict):
                self.errors.append(f"Invalid component contract: {component_name}")
                continue
            self._validate_component_file(component_name, component_contract)
            companion_contracts = component_contract.get("companion_files", {})
            if not isinstance(companion_contracts, dict):
                self.errors.append(f"Invalid companion files: {component_name}")
                continue
            for relative_path, expected_digest in companion_contracts.items():
                self._validate_digest(relative_path, expected_digest)

    def _validate_component_names(self, component_contracts: dict) -> None:
        discovered_component_names = set(component_contracts)
        missing_component_names = sorted(
            EXPECTED_COMPONENT_NAMES - discovered_component_names
        )
        unexpected_component_names = sorted(
            discovered_component_names - EXPECTED_COMPONENT_NAMES
        )
        if missing_component_names:
            self.errors.append(
                "Missing component contracts: "
                + ", ".join(missing_component_names)
            )
        if unexpected_component_names:
            self.errors.append(
                "Unexpected component contracts: "
                + ", ".join(unexpected_component_names)
            )

    def _validate_component_file(
        self,
        component_name: str,
        component_contract: dict,
    ) -> None:
        relative_path = component_contract.get("path")
        if not isinstance(relative_path, str):
            self.errors.append(f"Invalid component path: {component_name}")
            return
        component_path = self.package_root / relative_path
        if not component_path.is_file():
            self.errors.append(f"Missing component file: {relative_path}")
            return
        expected_digest = component_contract.get("sha256")
        if (
            not isinstance(expected_digest, str)
            or DIGEST_PATTERN.fullmatch(expected_digest) is None
        ):
            self.errors.append(
                f"Missing or invalid SHA-256 digest: {component_name}"
            )
            return
        self._validate_digest(relative_path, expected_digest)

    def _validate_digest(self, relative_path: str, expected_digest: object) -> None:
        component_path = self.package_root / relative_path
        if not component_path.is_file():
            self.errors.append(f"Missing digest file: {relative_path}")
            return
        actual_digest = hashlib.sha256(component_path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            self.errors.append(f"Digest mismatch: {relative_path}")

    def _validate_portability(self) -> None:
        entrypoint_path = self.package_root / "SKILL.md"
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
            "references/subagent-driven-development.md",
            "references/test-driven-development.md",
            "references/simplify-code.md",
            "references/requesting-code-review.md",
            "Resolve this file's real path",
            "references/CODE_STYLE.md",
            "references/NAMING.md",
            "templates/duty-report.md",
        )
        for required_fragment in required_fragments:
            if required_fragment not in entrypoint_text:
                self.errors.append(f"Missing package reference: {required_fragment}")

    def _validate_report(self) -> None:
        template_path = self.package_root / "templates/duty-report.md"
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
        f"{SKILL_NAME} {validator.package_version}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
