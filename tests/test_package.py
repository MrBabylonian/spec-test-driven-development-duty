from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip() if (PACKAGE_ROOT / "VERSION").exists() else ""
SELECTED_TDD_SHA256 = "39361054f58ecc8de9cac0f1364aee94e795a446030bb57595f7b7ca0c1ffbbe"
SIMPLIFY_CODE_SHA256 = "c259970bff23997a9b395f514af12723e33218fca97f529b5e0fa914ac72660e"
REQUESTING_CODE_REVIEW_SHA256 = "5a3a44a3667800e2dc836829c6b92fada51e6dc58ac144ec05fe59f47d6bcd84"
CODE_REVIEWER_TEMPLATE_SHA256 = "595d91d05d5ecba530bd52e1e53c5173d820ab5d4bc223eb7820d69a9ab1c403"
SUBAGENT_DRIVEN_DEVELOPMENT_SHA256 = "7120fad8ceb9860be267baee027ccb8d5e62629f055d044006cd169c7872d150"
CONTEXT_BUDGET_DISCIPLINE_SHA256 = "325d4f3b16db3215a1d7d8771b4c03af40cad62a468df5c44757c1e6366f2c9c"
GATES_TAXONOMY_SHA256 = "2740dbfb83cb58d2e8bffd6d2dca95c2dbccca3b60138dcb81b9be905554043a"


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


class PackageContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required_paths = (
            "plugin.json",
            "COMPONENTS.json",
            "VERSION",
            "README.md",
            "NOTICE.md",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".codex-plugin/plugin.json",
            ".agents/plugins/marketplace.json",
            "skills/spec-and-test-driven-development-duty/SKILL.md",
            "skills/spec-and-test-driven-development-duty/references/CODE_STYLE.md",
            "skills/spec-and-test-driven-development-duty/references/NAMING.md",
            "skills/spec-and-test-driven-development-duty/templates/duty-report.md",
            "skills/test-driven-development/SKILL.md",
            "skills/simplify-code/SKILL.md",
            "skills/requesting-code-review/SKILL.md",
            "skills/subagent-driven-development/SKILL.md",
            "vendor/test-driven-development/SKILL.md",
            "vendor/simplify-code/SKILL.md",
            "vendor/requesting-code-review/SKILL.md",
            "vendor/requesting-code-review/code-reviewer.md",
            "vendor/subagent-driven-development/SKILL.md",
            "vendor/subagent-driven-development/references/context-budget-discipline.md",
            "vendor/subagent-driven-development/references/gates-taxonomy.md",
            "scripts/validate_package.py",
        )
        missing_paths = [
            relative_path
            for relative_path in required_paths
            if not (PACKAGE_ROOT / relative_path).is_file()
        ]
        self.assertEqual([], missing_paths)

    def test_manifest_versions_match(self) -> None:
        manifest_paths = (
            "plugin.json",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".codex-plugin/plugin.json",
        )
        self.assertRegex(PACKAGE_VERSION, r"^\d+\.\d+\.\d+$")
        for relative_path in manifest_paths:
            manifest_payload = json.loads(
                (PACKAGE_ROOT / relative_path).read_text(encoding="utf-8")
            )
            if relative_path.endswith("marketplace.json"):
                discovered_versions = {
                    plugin_payload["version"]
                    for plugin_payload in manifest_payload["plugins"]
                    if "version" in plugin_payload
                }
                self.assertEqual({PACKAGE_VERSION}, discovered_versions)
            else:
                self.assertEqual(PACKAGE_VERSION, manifest_payload["version"])

    def test_skill_versions_match(self) -> None:
        components_payload = json.loads(
            (PACKAGE_ROOT / "COMPONENTS.json").read_text(encoding="utf-8")
        )
        component_contracts = components_payload["components"]
        for skill_path in sorted((PACKAGE_ROOT / "skills").glob("*/SKILL.md")):
            frontmatter_fields = FrontmatterReader.read(skill_path)
            self.assertEqual(skill_path.parent.name, frontmatter_fields["name"])
            expected_version = component_contracts[skill_path.parent.name]["version"]
            self.assertEqual(expected_version, frontmatter_fields["version"])

    def test_package_exposes_required_skill_set(self) -> None:
        discovered_names = {
            skill_path.parent.name
            for skill_path in (PACKAGE_ROOT / "skills").glob("*/SKILL.md")
        }
        self.assertEqual(
            {
                "requesting-code-review",
                "simplify-code",
                "spec-and-test-driven-development-duty",
                "subagent-driven-development",
                "test-driven-development",
            },
            discovered_names,
        )

    def test_entrypoint_is_host_neutral(self) -> None:
        entrypoint_text = (
            PACKAGE_ROOT
            / "skills/spec-and-test-driven-development-duty/SKILL.md"
        ).read_text(encoding="utf-8")
        forbidden_fragments = (
            "~/.hermes",
            ".resolved.md",
            "skill_view(",
            "hermes ",
            "software-development/test-driven-development",
            "verification-before-completion",
        )
        discovered_fragments = [
            fragment for fragment in forbidden_fragments if fragment in entrypoint_text
        ]
        self.assertEqual([], discovered_fragments)

    def test_entrypoint_owns_dependencies(self) -> None:
        entrypoint_text = (
            PACKAGE_ROOT
            / "skills/spec-and-test-driven-development-duty/SKILL.md"
        ).read_text(encoding="utf-8")
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
            self.assertIn(required_fragment, entrypoint_text)

    def test_report_template_forbids_postscripts(self) -> None:
        template_text = (
            PACKAGE_ROOT
            / "skills/spec-and-test-driven-development-duty/templates/duty-report.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Return only these seven fields.", template_text)
        self.assertIn("Do not append file lists", template_text)
        self.assertIn("`Issues encountered`", template_text)

    def test_tdd_skill_matches_selected_source(self) -> None:
        tdd_path = PACKAGE_ROOT / "vendor/test-driven-development/SKILL.md"
        packaged_digest = hashlib.sha256(tdd_path.read_bytes()).hexdigest()
        components_payload = json.loads(
            (PACKAGE_ROOT / "COMPONENTS.json").read_text(encoding="utf-8")
        )
        tdd_contract = components_payload["components"]["test-driven-development-source"]
        frontmatter_fields = FrontmatterReader.read(tdd_path)
        self.assertEqual(SELECTED_TDD_SHA256, tdd_contract["sha256"])
        self.assertEqual(tdd_contract["sha256"], packaged_digest)
        self.assertEqual("verbatim", tdd_contract["copy_mode"])
        self.assertEqual("1.1.0", tdd_contract["version"])
        self.assertEqual(tdd_contract["version"], frontmatter_fields["version"])
        self.assertEqual(
            "Hermes Agent (adapted from obra/superpowers)",
            frontmatter_fields["author"],
        )

    def test_tdd_directory_contains_selected_skill_only(self) -> None:
        tdd_directory = PACKAGE_ROOT / "vendor/test-driven-development"
        relative_paths = sorted(
            package_path.relative_to(tdd_directory).as_posix()
            for package_path in tdd_directory.rglob("*")
            if package_path.is_file()
        )
        self.assertEqual(["SKILL.md"], relative_paths)

    def test_tdd_wrapper_loads_selected_source(self) -> None:
        wrapper_text = (
            PACKAGE_ROOT / "skills/test-driven-development/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("../../vendor/test-driven-development/SKILL.md", wrapper_text)
        self.assertIn("Resolve this file's real path", wrapper_text)
        self.assertNotIn("Hermes Agent Integration", wrapper_text)

    def test_workflow_wrappers_load_selected_sources(self) -> None:
        wrapper_contracts = {
            "simplify-code": "../../vendor/simplify-code/SKILL.md",
            "requesting-code-review": "../../vendor/requesting-code-review/SKILL.md",
            "subagent-driven-development": "../../vendor/subagent-driven-development/SKILL.md",
        }
        for skill_name, required_path in wrapper_contracts.items():
            wrapper_text = (
                PACKAGE_ROOT / "skills" / skill_name / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn(required_path, wrapper_text)
            self.assertIn("Resolve this file's real path", wrapper_text)

    def test_vendored_workflow_sources_match(self) -> None:
        expected_digests = {
            "vendor/simplify-code/SKILL.md": SIMPLIFY_CODE_SHA256,
            "vendor/requesting-code-review/SKILL.md": REQUESTING_CODE_REVIEW_SHA256,
            "vendor/requesting-code-review/code-reviewer.md": CODE_REVIEWER_TEMPLATE_SHA256,
            "vendor/subagent-driven-development/SKILL.md": SUBAGENT_DRIVEN_DEVELOPMENT_SHA256,
            "vendor/subagent-driven-development/references/context-budget-discipline.md": CONTEXT_BUDGET_DISCIPLINE_SHA256,
            "vendor/subagent-driven-development/references/gates-taxonomy.md": GATES_TAXONOMY_SHA256,
        }
        for relative_path, expected_digest in expected_digests.items():
            actual_digest = hashlib.sha256(
                (PACKAGE_ROOT / relative_path).read_bytes()
            ).hexdigest()
            self.assertEqual(expected_digest, actual_digest)

    def test_entrypoint_enforces_mandatory_sequence(self) -> None:
        entrypoint_text = (
            PACKAGE_ROOT / "skills/spec-and-test-driven-development-duty/SKILL.md"
        ).read_text(encoding="utf-8")
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
            "simplify-code",
            "requesting-code-review",
        )
        for required_fragment in required_fragments:
            self.assertIn(required_fragment, entrypoint_text)
        self.assertLess(
            entrypoint_text.index("simplify-code"),
            entrypoint_text.index("requesting-code-review"),
        )

    def test_entrypoint_routes_subagent_implementation(self) -> None:
        entrypoint_text = (
            PACKAGE_ROOT / "skills/spec-and-test-driven-development-duty/SKILL.md"
        ).read_text(encoding="utf-8")
        required_fragments = (
            "subagent-driven-development",
            "classify task independence and file overlap",
            "fresh implementer",
            "spec-compliance review",
            "code-quality review",
            "controller-run vertical TDD",
            "Every delegated implementer and reviewer",
            "every file it references",
            "No isolated reviewer capability",
        )
        for required_fragment in required_fragments:
            self.assertIn(required_fragment, entrypoint_text)
        self.assertLess(
            entrypoint_text.index("subagent-driven-development"),
            entrypoint_text.index("simplify-code"),
        )

    def test_readme_defines_methodology_boundary(self) -> None:
        readme_text = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Methodology boundary", readme_text)
        self.assertIn("host and project inputs", readme_text)
        self.assertIn("does not auto-run", readme_text)

    def test_package_contains_no_symlinks(self) -> None:
        symlink_paths = [
            package_path.relative_to(PACKAGE_ROOT).as_posix()
            for package_path in PACKAGE_ROOT.rglob("*")
            if package_path.is_symlink()
        ]
        self.assertEqual([], symlink_paths)


if __name__ == "__main__":
    unittest.main()
