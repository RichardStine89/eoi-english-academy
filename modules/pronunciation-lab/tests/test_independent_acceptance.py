from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from benchmark_independent_acceptance import read_json, score, verdict


def digest(value):
    return sha256(value.encode()).hexdigest()


def case(key, speaker, *, expected="z", target="s", cohort="learner"):
    return {"id": key, "speaker": speaker, "prompt_sha256": digest(f"prompt {key}"),
            "audio_sha256": digest(f"audio {key}"), "cohort": cohort, "expected": expected, "target": target}


def review(reviewer, value):
    return {"reviewer": reviewer, "verdict": value}


class IndependentAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.development = [case("D", "development")]
        self.final = [case(str(i), f"voice{i % 5 if i < 25 else 5 + i % 5}",
                           cohort="learner" if i < 25 else "british_control")
                      for i in range(50)]
        self.a = {str(i): review("A", "target_error" if i < 25 else "valid") for i in range(50)}
        self.b = {str(i): review("B", "target_error" if i < 25 else "valid") for i in range(50)}
        self.predictions = {str(i): "target_alert" if i < 20 or i == 25 else "abstain" if i >= 45 else "clear"
                            for i in range(50)}

    def result(self):
        return score(self.development, self.final, self.a, self.b, {}, self.predictions)

    def test_boundaries_and_precision(self):
        row, = self.result()
        self.assertTrue(row["passes_technical_metrics"])
        self.assertEqual(row["effective_sensitivity"], .8)
        self.assertEqual(row["auditable_coverage"], .9)
        self.predictions["26"] = "target_alert"
        self.assertFalse(self.result()[0]["gates"]["precision_at_least_95"])
        self.predictions["26"] = "clear"
        self.predictions["19"] = "clear"
        for key in ("23", "24"):
            self.a[key]["verdict"] = self.b[key]["verdict"] = "valid"
        row, = self.result()
        self.assertEqual(row["precision"], .95)
        self.assertTrue(row["passes_technical_metrics"])

    def test_wrong_alert_and_positive_abstention(self):
        self.predictions["0"] = "other_alert"
        self.predictions["1"] = "abstain"
        row, = self.result()
        self.assertEqual(row["missed_effective"], 7)
        self.assertEqual(row["incorrect_or_unconfirmed_alerts"], 2)
        self.assertEqual(row["model_abstentions"], 6)
        self.assertFalse(row["gates"]["coverage_at_least_90"])

    def test_separation_by_each_identity(self):
        for field in ("speaker", "prompt_sha256", "audio_sha256"):
            with self.subTest(field=field):
                previous = self.final[0][field]
                self.final[0][field] = self.development[0][field]
                with self.assertRaisesRegex(ValueError, field):
                    self.result()
                self.final[0][field] = previous

    def test_disagreements_and_reviewers(self):
        self.assertEqual(verdict(review("A", "valid"), review("B", "target_error")), "ambiguous")
        result = verdict(review("A", "valid"), review("B", "target_error"), review("C", "valid"))
        self.assertEqual(result, "valid")
        with self.assertRaisesRegex(ValueError, "distinct"):
            verdict(review("A", "valid"), review(" a ", "target_error"))
        self.b["25"]["verdict"] = "target_error"
        row, = self.result()
        self.assertEqual(row["unresolved"], 1)
        self.assertEqual(row["auditable_coverage"], 44 / 50)

    def test_other_contrast_cannot_inherit_pass(self):
        self.final.append(case("different", "new", expected="θ", target="t"))
        self.a["different"] = review("A", "target_error")
        self.b["different"] = review("B", "target_error")
        self.predictions["different"] = "target_alert"
        first, second = self.result()
        self.assertTrue(first["passes_technical_metrics"])
        self.assertFalse(second["passes_technical_metrics"])

    def test_locked_bytes_and_duplicate_keys(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "example.json"
            path.write_text('{"id": 1, "id": 2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Repeated JSON key"):
                read_json(path)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                read_json(path, digest("different"))


if __name__ == "__main__":
    unittest.main()
