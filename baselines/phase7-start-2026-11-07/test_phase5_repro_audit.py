import unittest

import numpy as np

from phase5_repro_audit import equivalent


class Phase5ComparisonTests(unittest.TestCase):
    def test_nested_numeric_roundoff(self):
        equivalent({"a": [1.0, {"b": 2}]}, {"a": [1.0 + 1e-13, {"b": 2}]})

    def test_changed_metric_is_rejected(self):
        with self.assertRaises(AssertionError):
            equivalent({"mae": .5}, {"mae": .6})

    def test_changed_structure_is_rejected(self):
        with self.assertRaises(AssertionError):
            equivalent({"a": [1, 2]}, {"a": [1]})


if __name__ == "__main__":
    unittest.main()
