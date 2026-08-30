from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_VERSION = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip() if (PACKAGE_ROOT / "VERSION").exists() else ""


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
            "skills/test-driven-development/testing-anti-patterns.md",
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
        for skill_path in sorted((PACKAGE_ROOT / "skills").glob("*/SKILL.md")):
            frontmatter_fields = FrontmatterReader.read(skill_path)
            self.assertEqual(skill_path.parent.name, frontmatter_fields["name"])
            self.assertEqual(PACKAGE_VERSION, frontmatter_fields["version"])

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
            "../test-driven-development/SKILL.md",
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

    def test_package_contains_no_symlinks(self) -> None:
        symlink_paths = [
            package_path.relative_to(PACKAGE_ROOT).as_posix()
            for package_path in PACKAGE_ROOT.rglob("*")
            if package_path.is_symlink()
        ]
        self.assertEqual([], symlink_paths)


if __name__ == "__main__":
    unittest.main()
