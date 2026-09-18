from __future__ import annotations

import base64
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResumeStudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resume = json.loads((ROOT / "assets/example-resume.json").read_text(encoding="utf-8"))
        cls.legacy_resume = json.loads((ROOT / "assets/example-resume-v1.json").read_text(encoding="utf-8"))
        cls.ledger = json.loads((ROOT / "assets/example-ledger.json").read_text(encoding="utf-8"))
        cls.validator = load_module("resume_studio_validate", ROOT / "scripts/validate_resume.py")
        cls.renderer = load_module("resume_studio_render", ROOT / "scripts/render_resume.py")
        cls.renderer_v2 = load_module("resume_studio_render_v2", ROOT / "scripts/render_resume_v2.py")
        cls.alignment = load_module("resume_studio_alignment", ROOT / "scripts/validate_alignment.py")
        cls.intake = load_module("resume_studio_intake", ROOT / "scripts/assess_intake.py")

    def test_example_resume_passes(self) -> None:
        errors, _, counts = self.validator.validate_data(self.resume)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(counts["bullets"], 3)

    def test_example_ledger_is_strong(self) -> None:
        result = self.intake.assess(self.ledger)
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"], "strong")
        self.assertEqual(result["counts"]["complete_evidence_items"], 2)

    def test_one_complete_item_is_workable(self) -> None:
        ledger = json.loads(json.dumps(self.ledger, ensure_ascii=False))
        ledger["evidence_items"] = ledger["evidence_items"][:1]
        ledger["skills"] = ledger["skills"][:1]
        ledger["job_requirements"] = ledger["job_requirements"][:1]
        result = self.intake.assess(ledger)
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"], "workable")

    def test_missing_experience_is_blocked_with_one_question(self) -> None:
        ledger = json.loads(json.dumps(self.ledger, ensure_ascii=False))
        ledger["evidence_items"] = []
        ledger["skills"] = []
        ledger["job_requirements"] = []
        result = self.intake.assess(ledger)
        self.assertFalse(result["ok"])
        self.assertEqual(result["state"], "blocked")
        self.assertLessEqual(len(result["next_questions"]), 3)
        self.assertTrue(any(item["field"] == "evidence_items" for item in result["next_questions"]))

    def test_sensitive_fields_are_rejected(self) -> None:
        ledger = json.loads(json.dumps(self.ledger, ensure_ascii=False))
        ledger["basics"]["id_card"] = "000000000000000000"
        result = self.intake.assess(ledger)
        self.assertEqual(result["state"], "blocked")
        self.assertTrue(any("敏感字段" in message for message in result["errors"]))

    def test_invalid_jd_evidence_mapping_is_blocked(self) -> None:
        ledger = json.loads(json.dumps(self.ledger, ensure_ascii=False))
        ledger["job_requirements"][0]["evidence_ids"] = ["missing"]
        result = self.intake.assess(ledger)
        self.assertEqual(result["state"], "blocked")
        self.assertTrue(any("映射无效" in message for message in result["errors"]))

    def test_source_notes_never_render(self) -> None:
        rendered = self.renderer.make_html(self.resume)
        self.assertNotIn("合成测试数据；非真实人物", rendered)
        self.assertNotIn("source_note", rendered)
        self.assertIn("工作经历", rendered)
        self.assertLess(rendered.index("工作经历"), rendered.index("教育经历"))

    def test_legacy_v1_resume_still_renders(self) -> None:
        rendered = self.renderer.make_html(self.legacy_resume)
        self.assertIn('data-theme="swiss"', rendered)
        self.assertIn("工作经历", rendered)

    def test_targeted_alignment_example_passes(self) -> None:
        role = json.loads((ROOT / "assets/example-role-analysis.json").read_text(encoding="utf-8"))
        plan = json.loads((ROOT / "assets/example-resume-plan.json").read_text(encoding="utf-8"))
        errors, warnings, facts = self.alignment.validate_alignment(role, plan, self.resume)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(facts["visible_evidence_order"][0], "work-support-copilot")

    def test_all_layouts_have_distinct_dom(self) -> None:
        markers = {
            "classic-single-column": "resume-classic",
            "asymmetric-left-sidebar": "resume-left-sidebar",
            "sidebar-left-hero": "resume-sidebar-hero",
            "hero-header-blocks": "resume-hero-blocks",
            "hero-header-linear": "resume-hero-linear",
            "asymmetric-right-sidebar": "resume-right-sidebar",
            "tabular-structured": "resume-table",
            "banner-accent-flow": "resume-banner",
        }
        for layout, marker in markers.items():
            meta = self.renderer_v2.DESIGN_SYSTEM["layouts"][layout]
            rendered = self.renderer_v2.make_html(
                self.resume,
                layout=layout,
                density=meta["capacity"][0],
                render_profile=meta["render_profiles"][0],
            )
            self.assertIn(f'data-layout="{layout}"', rendered)
            self.assertIn(marker, rendered)

    def test_local_photo_is_embedded(self) -> None:
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
        resume = json.loads(json.dumps(self.resume, ensure_ascii=False))
        with tempfile.TemporaryDirectory() as temp_dir:
            photo = Path(temp_dir) / "portrait.png"
            photo.write_bytes(png)
            resume["basics"]["photo"] = {"enabled": True, "source": str(photo)}
            self.renderer.hydrate_photo(resume, Path(temp_dir))
            rendered = self.renderer.make_html(resume)
        self.assertIn('class="portrait"', rendered)
        self.assertIn("data:image/png;base64,", rendered)
        self.assertNotIn(str(photo), rendered)

    def test_renderer_cli_emits_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/render_resume.py"),
                    str(ROOT / "assets/example-resume.json"),
                    "--output-dir",
                    temp_dir,
                    "--basename",
                    "resume",
                    "--html-only",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((Path(temp_dir) / "resume.html").is_file())


if __name__ == "__main__":
    unittest.main()
