from itertools import product
import unittest

import numpy as np

from benchmark_ctc_contrasts import align_ctc, intervals, log_mass, refine_boundaries


def collapse(path):
    return [phone for i, phone in enumerate(path) if phone and (not i or phone != path[i - 1])]


class CtcContrastTests(unittest.TestCase):
    def test_path_marginal_matches_enumeration_including_repeated_phones(self):
        probabilities = np.array([[.23, .7, .07], [.8, .1, .1], [.19, .01, .8], [.2, .6, .2]])
        alternatives = [[1, 2], [1, 1], [2, 1]]
        expected = []
        for sequence in alternatives:
            expected.append(sum(np.prod(probabilities[np.arange(len(path)), path])
                                for path in product(range(3), repeat=4) if collapse(path) == sequence))
        np.testing.assert_allclose(np.exp(log_mass(np.log(probabilities), alternatives)), expected)

    def test_viterbi_requires_blank_between_repeated_labels(self):
        scores = np.log(np.array([[.05, .95], [.9, .1], [.2, .8]]))
        aligned = align_ctc(scores, [1, 1])
        self.assertEqual([run.tolist() for run in aligned], [[0], [2]])
        np.testing.assert_allclose(intervals(aligned, .0125, .02, .1), [.0025, .0325, .0625])
        self.assertIsNone(align_ctc(scores[:2], [1, 1]))

    def test_refinement_moves_only_vowel_consonant_transition(self):
        boundaries = np.array([0, .09, .18, .28])
        times = np.array([.08, .10, .16, .20])
        flux = np.array([0, 2, 0, 2])
        result = refine_boundaries(boundaries, ["S", "T", "AE"], times, flux)
        np.testing.assert_allclose(result, [0, .09, .20, .28])


if __name__ == "__main__":
    unittest.main()
