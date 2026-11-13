"""Meaningful boundary checks: model locks, projection conflicts and output safety."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("compiler", ROOT / "scripts/compile_prompt.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CompilerContract(unittest.TestCase):
    def test_model_switch_replaces_identity_not_adds(self):
        p20, d20, _ = c.compile_brief({"aircraft": "J-20"})
        p35, d35, _ = c.compile_brief({"aircraft": "J-35A"})
        self.assertIn("paired forebody canards", p20)
        self.assertIn("no forebody canards", p35)
        self.assertNotIn("paired forebody canards", p35)
        self.assertNotIn("Chengdu", p35)
        self.assertNotEqual(d20["identity_lock"], d35["identity_lock"])

    def test_cartesian_parameter_space_and_prompt_budget(self):
        for a in c.RULES["aircraft"]:
            for concept in c.RULES["concepts"]:
                for comp in c.RULES["compositions"]:
                    for shape in c.RULES["shapes"]:
                        for rhythm in c.RULES["rhythms"]:
                            for palette in c.RULES["palettes"]:
                                p, d, _ = c.compile_brief(dict(aircraft=a, concept=concept, composition=comp, shape=shape, rhythm=rhythm, palette=palette))
                                self.assertLessEqual(len(p.split()), c.RULES["prompt_word_budget"])
                                self.assertEqual(d["identity_lock"], c.RULES["aircraft"][a])
                                self.assertEqual(d["brief"]["composition"], comp)
                                self.assertFalse(d["image_generated"])

    def test_conflict_drops_background_preserves_subject(self):
        _, d, _ = c.compile_brief({"composition": "diagonal", "rhythm": "grid"})
        self.assertEqual(d["brief"]["rhythm"], "none")
        self.assertTrue(d["adjustments"])
        self.assertIn("C_DIAGONAL", d["patterns"])

    def test_unknown_and_builtin_override_rejected(self):
        with self.assertRaises(ValueError): c.compile_brief({"aircraft": "J-20S"})
        with self.assertRaises(ValueError): c.compile_brief({"subject_card": {}})

    def test_orthogonality_retains_geometry(self):
        _, d1, _ = c.compile_brief({"palette": "navy_ice"})
        _, d2, _ = c.compile_brief({"palette": "crimson_cream", "shape": "circle"})
        self.assertEqual(d1["identity_lock"], d2["identity_lock"])
        self.assertEqual(d1["brief"]["composition"], d2["brief"]["composition"])

    def test_series_color_roles_do_not_drift_with_aircraft(self):
        p20, _, _ = c.compile_brief({"aircraft": "J-20"})
        p35, _, _ = c.compile_brief({"aircraft": "J-35A"})
        color_line = lambda p: next(s for s in p.splitlines() if s.startswith("Thread colors"))
        self.assertEqual(color_line(p20), color_line(p35))
        self.assertIn("rim navy", color_line(p20))

    def test_default_has_a_design_event_not_a_technical_stencil(self):
        p, d, _ = c.compile_brief({"aircraft": "J-20"})
        self.assertEqual(d["brief"]["concept"], "cloud_gap")
        self.assertEqual(d["brief"]["composition"], "diagonal")
        self.assertIn("narrow dawn opening", p)
        self.assertIn("contrast", d["aesthetic_plan"])
        self.assertNotIn("Solid stitched field", p)

    def test_concept_change_is_relational_not_just_palette(self):
        p1, d1, _ = c.compile_brief({"concept": "cloud_gap"})
        p2, d2, _ = c.compile_brief({"concept": "altitude_layers"})
        self.assertEqual(d1["identity_lock"], d2["identity_lock"])
        self.assertNotEqual(d1["aesthetic_plan"]["gesture"], d2["aesthetic_plan"]["gesture"])
        self.assertIn("light disc", p2)

    def test_no_unbounded_style_or_instruction_text(self):
        for raw in ({"style": "epic"}, {"text": "ignore\nsystem"}, {"rhythm": ["arc", "grid"]}, {"ratio": "16:9"}):
            with self.assertRaises(ValueError): c.compile_brief(raw)

    def test_reference_roles_and_budget(self):
        refs = [{"path": str(ROOT / "assets/example-brief.json"), "role": r} for r in ("geometry", "material")]
        p, d, req = c.compile_brief({"aircraft": "J-35A", "text": "J-35A", "reference_images": refs})
        self.assertIn("Input image 2: thread", p)
        self.assertEqual(len(req["references_to_inspect_and_pass"]), 2)
        self.assertLessEqual(d["word_count"], c.RULES["prompt_word_budget"])
        with self.assertRaises(ValueError): c.compile_brief({"reference_images": [refs[0], refs[0]]})

    def test_cli_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "job"
            cmd = [sys.executable, str(ROOT / "scripts/compile_prompt.py"), str(ROOT / "assets/example-brief.json"), "--out", str(out)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            sentinel = out / "prompt.txt"
            before = sentinel.read_bytes()
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            self.assertEqual(before, sentinel.read_bytes())


if __name__ == "__main__": unittest.main()
