import unittest

import numpy as np

from ad_blockers_intrusion_v1 import grouped_split, prepare, fit_ridge, predict


class ExternalIntrusionTests(unittest.TestCase):
    def test_exact_answers_do_not_cross_holdout(self):
        _, _, groups = prepare()
        train, test = grouped_split(groups)
        self.assertFalse(set(groups[train]) & set(groups[test]))
        self.assertEqual(len(train) + len(test), 1511)

    def test_scaler_learns_training_only(self):
        x = np.array([[1., 2.], [3., 4.], [99., 100.]])
        y = np.array([-1., 1., 3.])
        fit = fit_ridge(x[:2], y[:2], 1.0)
        np.testing.assert_allclose(fit[1], [2., 3.])
        self.assertTrue(np.isfinite(predict(x[2:], fit)).all())


if __name__ == "__main__":
    unittest.main()
