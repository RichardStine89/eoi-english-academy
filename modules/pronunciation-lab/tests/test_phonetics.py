"""Check the evidence contract independently of model and corpus downloads."""

from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lab import brief_report
from phonetics import _unique_edit, _word_evidence, analyze_phonetics
from test_lab import METADATA


SAMPLE_RATE = 16_000
QUALITY = {"status": "measured", "quality": {"status": "usable"}}


def phone(ipa, probability):
    return SimpleNamespace(ipa=ipa, prob=probability, start=0.1, end=0.5)


def candidate(expected, observed, kind="substitution"):
    return {"kind": kind, "expected_ipa": expected, "heard_ipa": observed,
            "confidence": 0.8, "error_prob": 0.91, "start": 0.2, "end": 0.34}


class PhoneticContractTests(unittest.TestCase):
    def test_free_ctc_distinguishes_edits_and_ignores_accepted_variant(self):
        self.assertEqual(_unique_edit(["θ", "r", "i"], ["t", "r", "i"])["kind"], "substitution")
        self.assertEqual(_unique_edit(["f", "l", "i"], ["f", "i"])["kind"], "possible_omission")
        self.assertEqual(_unique_edit(["s", "p", "i"], ["ə", "s", "p", "i"])["kind"], "insertion")
        self.assertIsNone(_unique_edit(["w", "ɪ", "θ"], ["w", "ɪ", "ð"], "with"))
        self.assertIsNone(_unique_edit(["s", "s", "i"], ["s", "i"]))

    def test_named_hypothesis_has_time_and_stays_distinct_from_transcript(self):
        word = SimpleNamespace(text="sheep", start=0.07, end=0.52, present_prob=0.92, omitted=False,
                               phones=[phone("ʃ", 0.89), phone("i", 0.21), phone("p", 0.89)], syllables=[])
        evidence = _word_evidence(word, [candidate("i", "ɪ")], 0.8)
        self.assertEqual(evidence["expected_ipa"], "ʃiːp")
        self.assertIsNone(evidence["recognized"])
        finding, = evidence["findings"]
        self.assertEqual((finding["expected"], finding["observed"]), ("i", "ɪ"))
        self.assertLess(finding["start_seconds"], finding["end_seconds"])
        self.assertEqual(evidence["status"], "possible_deviation")

    def test_dialect_sensitive_and_insertion_outputs_are_not_promoted(self):
        word = SimpleNamespace(text="car", start=0.1, end=0.4, present_prob=0.91, omitted=False,
                               phones=[phone("k", 0.89), phone("ɑ", 0.75), phone("ɹ", 0.2)], syllables=[])
        evidence = _word_evidence(word, [candidate("ɹ", "", "missing"), candidate("ɑ", "ə", "extra")], 0.8)
        self.assertEqual(evidence["status"], "insufficient_evidence")
        self.assertEqual(evidence["findings"], [])

    def test_abstention_avoids_loading_model_on_unusable_or_uncontrolled_audio(self):
        test = np.zeros(SAMPLE_RATE * 2, dtype=np.float32)
        with patch("phonetics._scorer") as loader:
            self.assertEqual(analyze_phonetics(test, SAMPLE_RATE, "Hello.", {})["status"], "insufficient_evidence")
            self.assertEqual(analyze_phonetics(test, SAMPLE_RATE, None, QUALITY)["status"], "not_evaluated")
            loader.assert_not_called()

    def test_unavailable_model_preserves_acoustics_path(self):
        test = np.zeros(SAMPLE_RATE, dtype=np.float32)
        with patch("phonetics._scorer", side_effect=FileNotFoundError):
            result = analyze_phonetics(test, SAMPLE_RATE, "Hello.", QUALITY)
        self.assertEqual(result["status"], "not_evaluated")
        self.assertIsNone(result["temporal"])
        self.assertEqual(result["words"], [])

    def test_legacy_report_remains_readable_without_phonetics(self):
        report = {**METADATA, "attempt_number": 1, "created_at": "2026-01-01T11:00:00+00:00",
                  "acoustics": {"duration_seconds": 2.0, "quality": {"status": "usable"}, "metrics": {}},
                  "practice": []}
        self.assertIn("Informe anterior", brief_report(report))
        self.assertNotIn(METADATA["expected_text"], brief_report(report))
