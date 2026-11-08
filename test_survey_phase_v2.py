"""Leakage and diagnostic checks for the V2 survey experiment."""
import unittest

import numpy as np

from survey_phase_v2 import prepare, grouped_split, grouped_cv, segments, false_reassurance


class SurveyPhaseV2Tests(unittest.TestCase):
    def test_answer_vector_groups_never_cross_partitions(self):
        _, _, groups = prepare()
        train, test = grouped_split(groups, 49)
        self.assertEqual((len(train), len(test)), (670, 167))
        self.assertFalse(set(groups[train]) & set(groups[test]))

    def test_cv_does_not_read_held_out_targets(self):
        df, y, groups = prepare()
        train, test = grouped_split(groups, 49)
        original = grouped_cv(df, y, groups, train)
        changed = y.copy()
        changed[test] = 8 - changed[test]
        rerun = grouped_cv(df, changed, groups, train)
        np.testing.assert_allclose([row["out_of_fold_mae"] for row in original],
                                   [row["out_of_fold_mae"] for row in rerun])

    def test_false_reassurance_uses_agreement_and_neutral_anchors(self):
        y = np.array([2.0, 4.5, 5.0, 6.0])
        p = np.array([4.0, 4.5, 3.5, 4.8])
        self.assertEqual([x["n"] for x in segments(y, p).values()], [1, 1, 2])
        outcome = false_reassurance(y, p)
        self.assertEqual(outcome["high_predicted_below_neutral_4"], 1)
        self.assertEqual(outcome["high_predicted_below_agreement_5"], 2)


if __name__ == "__main__":
    unittest.main()
