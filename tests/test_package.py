from __future__ import annotations

import hashlib
import json
import re
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.validate_package import PackageValidationError, PackageValidator


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
SKILL_NAME = "spec-test-driven-development-duty"
SUPPORTING_COMPONENT_NAMES = {
    "requesting-code-review",
    "simplify-code",
    "subagent-driven-development",
    "test-driven-development",
}


class MutablePackageFixture:
    def __init__(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.package_root = (
            Path(self.temporary_directory.name) / "skill-package"
        )
        shutil.copytree(
            PACKAGE_ROOT,
            self.package_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def remove_component(self, component_name: str) -> None:
        components_payload = self._read_components()
        del components_payload["components"][component_name]
        self._write_components(components_payload)

    def remove_component_field(
        self,
        component_name: str,
        field_name: str,
    ) -> None:
        components_payload = self._read_components()
        del components_payload["components"][component_name][field_name]
        self._write_components(components_payload)

    def remove_component_field_if_present(
        self,
        component_name: str,
        field_name: str,
    ) -> None:
        components_payload = self._read_components()
        component_contract = components_payload["components"][component_name]
        if field_name in component_contract:
            del component_contract[field_name]
        self._write_components(components_payload)

    def add_component(self, component_name: str) -> None:
        components_payload = self._read_components()
        components_payload["components"][component_name] = {
            "path": f"references/{component_name}.md",
            "role": "supporting-reference",
            "source": f"installed:{component_name}",
            "version": "unversioned",
            "sha256": "0" * 64,
        }
        self._write_components(components_payload)

    def _read_components(self) -> dict:
        return json.loads(
            (self.package_root / "COMPONENTS.json").read_text(encoding="utf-8")
        )

    def _write_components(self, components_payload: dict) -> None:
        serialized_components = json.dumps(components_payload, indent=2) + "\n"
        (self.package_root / "COMPONENTS.json").write_text(
            serialized_components,
            encoding="utf-8",
        )


class FrontmatterReader:
    @staticmethod
    def read(document_path: Path) -> dict[str, str]:
        document_text = document_path.read_text(encoding="utf-8")
        if not document_text.startswith("---\n"):
            raise AssertionError(f"Missing frontmatter: {document_path}")
        frontmatter_text = document_text[4:].split("\n---\n", 1)[0]
        parsed_fields: dict[str, str] = {}
        for source_line in frontmatter_text.splitlines():
            match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.+)$", source_line)
            if match:
                parsed_fields[match.group(1)] = match.group(2).strip()
        return parsed_fields


class PackageValidatorRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package_fixture = MutablePackageFixture()

    def tearDown(self) -> None:
        self.package_fixture.close()

    def test_pristine_package_passes_validation(self) -> None:
        PackageValidator(self.package_fixture.package_root).validate()

    def test_missing_supporting_component_fails_validation(self) -> None:
        self.package_fixture.remove_component("test-driven-development")

        with self.assertRaisesRegex(
            PackageValidationError,
            "Missing component contracts: test-driven-development",
        ):
            PackageValidator(self.package_fixture.package_root).validate()

    def test_missing_supporting_digest_fails_validation(self) -> None:
        self.package_fixture.remove_component_field(
            "test-driven-development",
            "sha256",
        )

        with self.assertRaisesRegex(
            PackageValidationError,
            "Missing or invalid SHA-256 digest: test-driven-development",
        ):
            PackageValidator(self.package_fixture.package_root).validate()

    def test_missing_entrypoint_digest_fails_validation(self) -> None:
        self.package_fixture.remove_component_field_if_present(
            SKILL_NAME,
            "sha256",
        )

        with self.assertRaisesRegex(
            PackageValidationError,
            f"Missing or invalid SHA-256 digest: {SKILL_NAME}",
        ):
            PackageValidator(self.package_fixture.package_root).validate()

    def test_unexpected_component_fails_validation(self) -> None:
        self.package_fixture.add_component("bogus-component")

        with self.assertRaisesRegex(
            PackageValidationError,
            "Unexpected component contracts: bogus-component",
        ):
            PackageValidator(self.package_fixture.package_root).validate()


class SkillPackageContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required_paths = (
            "SKILL.md",
            "COMPONENTS.json",
            "NOTICE.md",
            "README.md",
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
            "scripts/validate_package.py",
            "templates/duty-report.md",
        )
        missing_paths = [
            relative_path
            for relative_path in required_paths
            if not (PACKAGE_ROOT / relative_path).is_file()
        ]
        self.assertEqual([], missing_paths)

    def test_plugin_packaging_is_absent(self) -> None:
        forbidden_paths = (
            "plugin.json",
            ".agents",
            ".claude-plugin",
            ".codex-plugin",
            ".cursor-plugin",
            "skills",
            "vendor",
        )
        discovered_paths = [
            relative_path
            for relative_path in forbidden_paths
            if (PACKAGE_ROOT / relative_path).exists()
        ]
        self.assertEqual([], discovered_paths)

    def test_root_skill_frontmatter_matches_install_directory(self) -> None:
        frontmatter_fields = FrontmatterReader.read(PACKAGE_ROOT / "SKILL.md")
        self.assertEqual(SKILL_NAME, frontmatter_fields["name"])
        self.assertEqual(PACKAGE_VERSION, frontmatter_fields["version"])
        self.assertTrue(frontmatter_fields["description"])

    def test_component_files_match_recorded_digests(self) -> None:
        components_payload = json.loads(
            (PACKAGE_ROOT / "COMPONENTS.json").read_text(encoding="utf-8")
        )
        self.assertEqual(PACKAGE_VERSION, components_payload["package_version"])
        component_contracts = components_payload["components"]
        self.assertEqual(
            "SKILL.md",
            component_contracts[SKILL_NAME]["path"],
        )
        self.assertEqual(
            SUPPORTING_COMPONENT_NAMES | {SKILL_NAME},
            set(component_contracts),
        )
        for component_contract in component_contracts.values():
            self._assert_recorded_digest(component_contract)
            companion_contracts = component_contract.get("companion_files", {})
            for relative_path, expected_digest in companion_contracts.items():
                self._assert_digest(relative_path, expected_digest)

    def test_entrypoint_owns_supporting_workflows(self) -> None:
        entrypoint_text = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required_fragments = (
            "references/subagent-driven-development.md",
            "references/test-driven-development.md",
            "references/simplify-code.md",
            "references/requesting-code-review.md",
            "references/CODE_STYLE.md",
            "references/NAMING.md",
            "templates/duty-report.md",
            "Resolve this file's real path",
        )
        for required_fragment in required_fragments:
            self.assertIn(required_fragment, entrypoint_text)

    def test_entrypoint_enforces_mandatory_sequence(self) -> None:
        entrypoint_text = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required_fragments = (
            "If neither specifications nor features are provided",
            "ask the user to provide them",
            "If any ambiguity remains",
            "ask all clarification questions",
            "Only the engineer's answers close ambiguity",
            "Before every stage",
            "AGENTS.md",
            "every file it references",
            "No exception",
            "fresh implementer",
            "spec-compliance review",
            "code-quality review",
            "controller-run vertical TDD",
            "No isolated reviewer capability",
        )
        for required_fragment in required_fragments:
            self.assertIn(required_fragment, entrypoint_text)
        self.assertLess(
            entrypoint_text.index("references/simplify-code.md"),
            entrypoint_text.index("references/requesting-code-review.md"),
        )

    def test_supporting_reference_paths_are_flat(self) -> None:
        requesting_review_text = (
            PACKAGE_ROOT / "references/requesting-code-review.md"
        ).read_text(encoding="utf-8")
        subagent_development_text = (
            PACKAGE_ROOT / "references/subagent-driven-development.md"
        ).read_text(encoding="utf-8")
        self.assertIn("adjacent `code-reviewer.md`", requesting_review_text)
        self.assertIn("adjacent references", subagent_development_text)
        self.assertNotIn(
            "requesting-code-review/code-reviewer.md",
            requesting_review_text,
        )
        self.assertNotIn(
            "references/context-budget-discipline.md",
            subagent_development_text,
        )

    def test_report_template_forbids_postscripts(self) -> None:
        template_text = (
            PACKAGE_ROOT / "templates/duty-report.md"
        ).read_text(encoding="utf-8")
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
            self.assertEqual(1, template_text.count(required_field))
        self.assertIn("Return only these seven fields.", template_text)
        self.assertIn("Do not append file lists", template_text)

    def test_readme_documents_regular_skill_installation(self) -> None:
        readme_text = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "~/.cursor/skills/spec-test-driven-development-duty/SKILL.md",
            readme_text,
        )
        self.assertIn(
            "~/.claude/skills/spec-test-driven-development-duty/SKILL.md",
            readme_text,
        )
        self.assertIn(
            "~/.codex/skills/spec-test-driven-development-duty/SKILL.md",
            readme_text,
        )
        self.assertIn("## Methodology boundary", readme_text)
        self.assertNotIn("~/.cursor/plugins/local", readme_text)

    def test_package_contains_no_symbolic_links(self) -> None:
        symbolic_link_paths = [
            package_path.relative_to(PACKAGE_ROOT).as_posix()
            for package_path in PACKAGE_ROOT.rglob("*")
            if package_path.is_symlink()
        ]
        self.assertEqual([], symbolic_link_paths)

    def _assert_recorded_digest(self, component_contract: dict) -> None:
        expected_digest = component_contract["sha256"]
        self.assertIsInstance(expected_digest, str)
        self.assertRegex(expected_digest, r"^[0-9a-f]{64}$")
        self._assert_digest(component_contract["path"], expected_digest)

    def _assert_digest(self, relative_path: str, expected_digest: str) -> None:
        actual_digest = hashlib.sha256(
            (PACKAGE_ROOT / relative_path).read_bytes()
        ).hexdigest()
        self.assertEqual(expected_digest, actual_digest)


if __name__ == "__main__":
    unittest.main()
