"""Focused finite-sample calibration checks for Phase 4."""
import unittest

import numpy as np

from survey_phase_v3_uncertainty import finite_sample_quantile, wilson_interval
from survey_phase_v2 import grouped_cv, grouped_split, prepare


class ConformalAuditTests(unittest.TestCase):
    def test_finite_sample_order_statistic(self):
        self.assertEqual(finite_sample_quantile(np.arange(1, 20), .1), 18.0)

    def test_too_small_calibration_is_rejected(self):
        with self.assertRaises(ValueError):
            finite_sample_quantile(np.arange(1, 6), .1)

    def test_wilson_bounds(self):
        lo, hi = wilson_interval(9, 10)
        self.assertTrue(0 < lo < .9 < hi < 1)

    def test_model_selection_excludes_calibration_and_outer_holdout_targets(self):
        df, y, groups = prepare()
        outer_train, outer_test = grouped_split(groups, 49)
        fit_local, cal_local = grouped_split(groups[outer_train], 4905)
        fit_idx, cal_idx = outer_train[fit_local], outer_train[cal_local]
        self.assertFalse(set(groups[fit_idx]) & set(groups[cal_idx]))
        original = grouped_cv(df, y, groups, fit_idx)
        changed = y.copy()
        changed[np.concatenate((cal_idx, outer_test))] = 8 - changed[np.concatenate((cal_idx, outer_test))]
        repeated = grouped_cv(df, changed, groups, fit_idx)
        np.testing.assert_allclose([r["out_of_fold_mae"] for r in original],
                                   [r["out_of_fold_mae"] for r in repeated])


if __name__ == "__main__":
    unittest.main()
