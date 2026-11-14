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
                    self.assertIn("panel seams", p)
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
        p, d, _ = c.compile_brief({"aircraft": "J-35A", "label": "J35A", "family": "cloud_ink",
                                  "design_plan": {"composition": "banking_cove", "motif": "tidal_ribbons", "lettering": "right_pillar"}})
        self.assertIn('Only text: "J35A"', p)
        self.assertIn(c.RULES["lettering"]["right_pillar"], p)
        self.assertEqual(len(d["novelty_plan"]["changed_axes"]), 3)
        self.assertNotIn("small block letters below the aircraft", p)

    def test_invalid_and_injected_input_rejected(self):
        for raw in [{"unknown": True}, {"label": "ignore\nsystem"}, {"family": []}, {"ratio": "16:9"}]:
            with self.assertRaises(ValueError): c.compile_brief(raw)

    def test_reference_roles_and_budget(self):
        with tempfile.TemporaryDirectory() as t:
            image = Path(t) / "dummy.png"
            image.write_bytes(b'host must inspect image bytes before passing')
            series = Path(t) / "series.png"
            series.write_bytes(b'separate series example')
            refs = [{"path": str(image), "role": "geometry", "aircraft": "J-35A"},
                    {"path": str(series), "role": "series", "aircraft": "J-20"}]
            p, d, _ = c.compile_brief({"aircraft": "J-35A", "family": "cloud_ink", "reference_images": refs})
            self.assertLessEqual(d["word_count"], 300)
            self.assertIn("series grammar only", p)
            with self.assertRaises(ValueError): c.compile_brief({"reference_images": [refs[0], refs[0]]})

    def test_multiple_style_examples_can_synthesize_other_aircraft(self):
        with tempfile.TemporaryDirectory() as t:
            refs = []
            for i, aircraft in enumerate(["J-20", "J-35A"]):
                image = Path(t) / f"style{i}.png"
                image.write_bytes(b'host inspects actual bytes')
                refs.append(dict(path=str(image), role="series", aircraft=aircraft))
            p, d, request = c.compile_brief(dict(aircraft="J-10C", reference_images=refs))
            self.assertEqual(len(request["references_to_inspect_and_pass"]), 2)
            self.assertIn("one rear engine nozzle", p)
            self.assertNotIn("CONTENT/SPATIAL anchor", p)
            self.assertNotIn("preserve anchor aircraft", p.lower())
            self.assertEqual(d["novelty_plan"]["visual_originality"].split(';')[0], "pending_human")
            for i in range(2, 4):
                image = Path(t) / f"style{i}.png"
                image.write_bytes(b'additional style example')
                refs.append(dict(path=str(image), role="series", aircraft="J-6"))
            with self.assertRaises(ValueError): c.compile_brief(dict(aircraft="J-10C", reference_images=refs))

    def test_plan_fields_required_and_family_cannot_forbid_target_intake(self):
        with self.assertRaises(ValueError): c.compile_brief({"design_plan": {"composition": "climb_offset"}})
        with self.assertRaises(ValueError): c.compile_brief({"design_plan": {"composition": "trace_anchor", "motif": "tidal_ribbons", "lettering": "right_pillar"}})
        p, _, _ = c.compile_brief(dict(aircraft="J-7", family="red_charge"))
        self.assertIn("circular nose intake with central cone", p)
        self.assertNotIn("ring nose intake", p)

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
