"""Numerical checks for the isolated Criteo benchmark helpers."""
import unittest

import numpy as np

from criteo_visit_uplift import fit_logistic, predict
from criteo_uplift_validation import ranking_gain


class CriteoBenchmarkTests(unittest.TestCase):
    def test_logistic_fit_is_finite_and_improves_held_out_loss(self):
        rng = np.random.default_rng(19)
        x = rng.normal(size=(3000, 2))
        true_probability = 1 / (1 + np.exp(-(-2 + 1.2 * x[:, 0] - .7 * x[:, 1])))
        y = rng.binomial(1, true_probability)
        beta, steps = fit_logistic(x[:2400], y[:2400])
        forecast = predict(x[2400:], beta)
        baseline = np.full(len(forecast), y[:2400].mean())

        def loss(p):
            return float(-np.mean(y[2400:] * np.log(p) + (1 - y[2400:]) * np.log1p(-p)))

        self.assertTrue(np.isfinite(beta).all())
        self.assertLess(steps, 50)
        self.assertGreater(float(np.std(forecast)), .01)
        self.assertLess(loss(forecast), loss(baseline))

    def test_uplift_gain_requires_both_arms(self):
        y = np.array([0, 1, 0, 1])
        t = np.array([0, 0, 0, 0])
        with self.assertRaises(ValueError):
            ranking_gain(y, t, np.array([.1, .2, .3, .4]))


if __name__ == "__main__":
    unittest.main()
