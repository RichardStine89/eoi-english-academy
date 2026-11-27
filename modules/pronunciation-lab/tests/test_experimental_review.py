"""Exercise the listening-only selector without models, recordings or student data."""

from copy import deepcopy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experimental_review import ReviewUnavailable, select_fragment
from lab_app import LabApp


AUDIO = (np.zeros(16_000, dtype=np.float32), 16_000)
WORD = {
    "expected": "easy",
    "alignment_supported": True,
    "reference_phones": ["i", "z", "i"],
    "aligned_phones": [
        {"expected_model_phone": "i", "start_seconds": 0.05, "end_seconds": 0.17},
        {"expected_model_phone": "z", "start_seconds": 0.17, "end_seconds": 0.27},
        {"expected_model_phone": "i", "start_seconds": 0.27, "end_seconds": 0.4},
    ],
}


class ExperimentalReviewTests(unittest.TestCase):
    def test_narrow_agreement_selects_only_a_fragment_index(self):
        words = [deepcopy(WORD)]
        with patch("experimental_review._decode", return_value=[["IY", 0.09], ["S", 0.2], ["IY", 0.33]]):
            self.assertEqual(select_fragment(AUDIO, words), 0)
            self.assertIsNone(select_fragment(AUDIO, words * 2))
        self.assertEqual(words, [WORD])

    def test_context_or_known_reference_variant_stops_before_worker(self):
        final = deepcopy(WORD)
        final["reference_phones"].pop()
        final["aligned_phones"].pop()
        variants = {**WORD, "reference_ipa_variants": ["ˈiːzi", "ˈiːsi"]}
        with patch("experimental_review._decode") as worker:
            self.assertIsNone(select_fragment(AUDIO, [final, variants]))
            worker.assert_not_called()

    def test_disagreed_vowels_and_neutral_result(self):
        with patch("experimental_review._decode", return_value=[["IY", 0.09], ["S", 0.23], ["IY", 0.6]]):
            self.assertEqual(LabApp._review_audio(AUDIO, [WORD]), ("experimental_review", None))
        with patch("experimental_review._decode", side_effect=ReviewUnavailable("Escucha manual.")):
            self.assertEqual(LabApp._review_audio(AUDIO, [WORD]), ("review_unavailable", "Escucha manual."))

    def test_disabled_review_never_starts_a_worker(self):
        app = SimpleNamespace(busy=False, review_enabled=Mock(), _start_job=Mock(),
                              audio=AUDIO, report={"phonetics": {}}, _review_audio=Mock())
        app.review_enabled.get.return_value = False
        LabApp._run_review(app)
        app._start_job.assert_not_called()
        app.review_enabled.get.return_value = True
        LabApp._run_review(app)
        app._start_job.assert_called_once()


if __name__ == "__main__":
    unittest.main()
