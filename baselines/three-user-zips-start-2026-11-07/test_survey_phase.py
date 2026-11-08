"""Checks for the independent respondent survey experiment."""
import unittest

import numpy as np

from survey_phase_v1 import INTRUSION, SAV, fit_ridge, predict_ridge, read_sav, respondent_survey


class SurveyPhaseTests(unittest.TestCase):
    @unittest.skipUnless(SAV.exists(), "The secondary SPSS source is unavailable")
    def test_direct_intrusion_items_are_the_target_only(self):
        df = read_sav(SAV)
        np.testing.assert_allclose(df[INTRUSION].mean(axis=1), df["ITV_mean"])
        report, _ = respondent_survey()
        features = report["feature_sets"]["predeclared_combined"]
        self.assertTrue(set(features).isdisjoint(INTRUSION + ["ITV_mean", "AAB1", "AAB2", "AAB3", "AAB4"]))
        self.assertEqual(report["train_rows"] + report["test_rows"], 837)

    def test_ridge_uses_training_statistics(self):
        x_train = np.array([[0.], [1.], [2.], [3.]])
        y_train = np.array([1., 2., 3., 4.])
        fit = fit_ridge(x_train, y_train)
        self.assertAlmostEqual(float(fit[1][0]), 1.5)
        before = predict_ridge(np.array([[2.]]), fit)
        predict_ridge(np.array([[1000.]]), fit)
        after = predict_ridge(np.array([[2.]]), fit)
        np.testing.assert_allclose(before, after)


if __name__ == "__main__":
    unittest.main()
