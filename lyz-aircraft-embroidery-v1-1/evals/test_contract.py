import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load("compile_prompt")
s = load("score_blind")


class RuntimeContract(unittest.TestCase):
    def test_family_model_pose_cross_product(self):
        for aircraft in c.RULES["aircraft"]:
            for family in c.RULES["families"]:
                for pose in c.RULES["poses"]:
                    p, d, _ = c.compile_brief(dict(aircraft=aircraft, family=family, pose=pose))
                    self.assertLessEqual(d["word_count"], 300)
                    self.assertEqual(d["identity_lock"], c.RULES["aircraft"][aircraft])
                    self.assertIn("omit panel seams", p)
                    self.assertIn('Only text: "'+aircraft.replace('-', '')+'"', p)

    def test_wrong_aircraft_or_appendage_not_transferred(self):
        p, _, _ = c.compile_brief({"aircraft": "J-35A"})
        self.assertIn("no forebody canards", p)
        self.assertNotIn("paired forebody canards", p)
        with self.assertRaises(ValueError): c.compile_brief({"aircraft": "J-20S"})

    def test_oblique_grid_is_not_automatically_deleted(self):
        p, _, _ = c.compile_brief({"family": "kinetic_grid", "pose": "dorsal_left"})
        self.assertIn("perspective grid", p)
        self.assertIn("three-quarter", p)

    def test_text_is_integrated_and_not_footer(self):
        p, _, _ = c.compile_brief({"label": "J35A", "family": "cloud_ink"})
        self.assertIn('Only text: "J35A"', p)
        self.assertIn("lower-right", p)
        self.assertNotIn("small block letters below the aircraft", p)

    def test_invalid_and_injected_input_rejected(self):
        for raw in [{"unknown": True}, {"label": "ignore\nsystem"}, {"family": []}, {"ratio": "16:9"}]:
            with self.assertRaises(ValueError): c.compile_brief(raw)

    def test_reference_roles_and_budget(self):
        with tempfile.TemporaryDirectory() as t:
            image = Path(t) / "dummy.png"
            image.write_bytes(b'host must inspect image bytes before passing')
            refs = [{"path": str(image), "role": role, "aircraft": "J-35A"} for role in ("geometry", "series")]
            p, d, _ = c.compile_brief({"aircraft": "J-35A", "family": "cloud_ink", "reference_images": refs})
            self.assertLessEqual(d["word_count"], 300)
            self.assertIn("COLOR/TEXTILE authority only", p)
            with self.assertRaises(ValueError): c.compile_brief({"reference_images": [refs[0], refs[0]]})

    def test_foreign_geometry_rejected_but_style_allowed(self):
        with tempfile.TemporaryDirectory() as t:
            image = Path(t) / "dummy.png"
            image.write_bytes(b'host must inspect actual images')
            ref = {"path": str(image), "role": "geometry", "aircraft": "J-35A"}
            with self.assertRaises(ValueError): c.compile_brief({"aircraft": "J-20", "reference_images": [ref]})
            ref["role"] = "series"
            p, _, _ = c.compile_brief({"aircraft": "J-20", "reference_images": [ref]})
            self.assertIn("do not borrow its aircraft", p)

    def test_identity_negatives_and_topology_reach_actual_request(self):
        for aircraft, card in c.RULES["aircraft"].items():
            p, _, request = c.compile_brief({"aircraft": aircraft})
            for forbidden in card["avoid_features"]:
                self.assertIn(forbidden, request["prompt"])
            self.assertIn(card["topology"], p)

    def test_outputs_never_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            args = [sys.executable, str(ROOT/'scripts/compile_prompt.py'), str(ROOT/'assets/example-brief.json'), '--out', t]
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
            original = (Path(t)/'prompt.txt').read_bytes()
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 2)
            self.assertEqual((Path(t)/'prompt.txt').read_bytes(), original)


class BlindScoring(unittest.TestCase):
    def fixture(self):
        key = {'session':'synthetic-test','nonce':'test-only','jobs':[{'label':label,'version':version,'task_id':task} for task, labels in [('T1','AB'),('T2','CD'),('T3','EF')] for label, version in zip(labels, ['baseline','candidate'])]}
        ratings = {'session':key['session'],'assignment_commitment_sha256':s.commitment(key),'ratings':{label:{d:(2 if label in 'ACE' else 4) for d in s.DIMENSIONS} for label in 'ABCDEF'}}
        return ratings, key

    def test_no_verdict_without_complete_human_scores(self):
        r, k = self.fixture()
        r['ratings']['A']['text'] = None
        with self.assertRaises(ValueError): s.compare(r, k)

    def test_tampered_assignment_rejected(self):
        r, k = self.fixture()
        k['nonce'] = 'changed'
        with self.assertRaises(ValueError): s.compare(r, k)

    def test_structure_failure_cannot_be_averaged_away(self):
        r, k = self.fixture()
        r['ratings']['B']['structure'] = 1
        result = s.compare(r, k)
        self.assertFalse(result['iteration_success_under_preregistered_rule'])

    def test_synthetic_comparison_arithmetic(self):
        r, k = self.fixture()
        result = s.compare(r, k)
        self.assertEqual(result['candidate_paired_wins'], 3)
        self.assertEqual(result['delta'], 2)
        self.assertTrue(result['iteration_success_under_preregistered_rule'])

    def test_bool_or_missing_dimension_not_a_rating(self):
        r, k = self.fixture()
        r['ratings']['A']['structure'] = True
        with self.assertRaises(ValueError): s.compare(r, k)

    def test_qa_export_cannot_reveal_real_assignment(self):
        r, k = self.fixture()
        r['qa'] = True
        with self.assertRaises(ValueError): s.compare(r, k)


if __name__ == '__main__': unittest.main()
