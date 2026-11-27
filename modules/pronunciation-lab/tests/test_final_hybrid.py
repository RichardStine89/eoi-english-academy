import unittest

from benchmark_final_hybrid import ADVANCED, ADVISORY, decision, qualifies
from benchmark_sibilant_acoustics import summarize


class FinalHybridTests(unittest.TestCase):
    def test_thresholds_are_separate_and_inclusive(self):
        advisory = {"effective_sensitivity": .60, "precision": .90, "coverage": .80}
        advanced = {"effective_sensitivity": .80, "precision": .95, "coverage": .90}
        self.assertTrue(qualifies(advisory, ADVISORY))
        self.assertFalse(qualifies(advisory, ADVANCED))
        self.assertTrue(qualifies(advanced, ADVANCED))
        self.assertFalse(qualifies({**advanced, "precision":None}, ADVISORY))

    def test_vote_and_cascade_keep_missing_evidence_unresolved(self):
        score = {"beam": True, "cupe": None, "neural": .99}
        self.assertIsNone(decision(score, ("vote", "cupe", .50, .75)))
        self.assertIsNone(decision(score, ("cascade", "cupe", .60, True)))
        score["cupe"] = .15
        self.assertIsNone(decision(score, ("cascade", "cupe", .60, False)))
        self.assertFalse(decision(score, ("cascade", "cupe", .60, True)))

    def test_abstaining_from_an_error_counts_as_effective_miss(self):
        rows = [{"positive":True}, {"positive":False}]
        metrics = summarize(rows, lambda row: None if row["positive"] else False)
        self.assertEqual(metrics["fn_effective"], 1)
        self.assertEqual(metrics["coverage"], .50)
        self.assertIsNone(metrics["precision"])


if __name__ == "__main__":
    unittest.main()
