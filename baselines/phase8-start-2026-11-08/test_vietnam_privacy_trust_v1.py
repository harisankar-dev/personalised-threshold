import unittest

from vietnam_privacy_trust_v1 import prepare, SCALES


class VietnamSurveyTests(unittest.TestCase):
    def test_prepared_data_excludes_screening_and_ambiguous_multi_select(self):
        data = prepare()
        self.assertEqual(len(data), 467)
        self.assertEqual(set(data.columns), {"age", "gender", "occupation", "q4", *SCALES})
        self.assertFalse(data.isna().any().any())


if __name__ == "__main__":
    unittest.main()
