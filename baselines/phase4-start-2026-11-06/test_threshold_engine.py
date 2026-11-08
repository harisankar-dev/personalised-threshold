"""Decision-logic checks using hypothetical values, not study observations."""
import unittest

from threshold_engine import LevelEstimate, REQUIRED_EVIDENCE, current_dataset_status, recommend


def estimate(level, engagement, intrusion, engagement_lower=None, intrusion_upper=None):
    return LevelEstimate(
        level=level, engagement=engagement,
        engagement_lower=engagement if engagement_lower is None else engagement_lower,
        engagement_upper=engagement,
        intrusion=intrusion, intrusion_lower=intrusion,
        intrusion_upper=intrusion if intrusion_upper is None else intrusion_upper,
    )


VALID_EVIDENCE = {name: True for name in REQUIRED_EVIDENCE}


class ThresholdEngineTests(unittest.TestCase):
    def test_current_data_abstains(self):
        result = current_dataset_status()
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertIsNone(result["recommended_level"])
        self.assertIn("direct_intrusiveness_labels", result["missing"])

    def test_missing_evidence_prevents_recommendation(self):
        result = recommend([estimate(0, .2, .1)], eligible_levels={0},
                           max_intrusion_risk=.5, evidence={})
        self.assertEqual(result["status"], "insufficient_evidence")

    def test_consent_eligibility_is_hard_constraint(self):
        result = recommend([estimate(0, .2, .1), estimate(4, .9, .2)],
                           eligible_levels={0, 4}, max_intrusion_risk=.5,
                           evidence=VALID_EVIDENCE)
        self.assertEqual(result["recommended_level"], 0)
        self.assertEqual(result["eligible_levels"], [0])

    def test_upper_risk_bound_and_lower_engagement_bound(self):
        result = recommend([
            estimate(0, .2, .1, engagement_lower=.18),
            estimate(1, .6, .3, engagement_lower=.45, intrusion_upper=.4),
            estimate(2, .8, .4, engagement_lower=.7, intrusion_upper=.7),
        ], eligible_levels={0, 1, 2}, consent_verified=True, max_intrusion_risk=.5,
            evidence=VALID_EVIDENCE)
        self.assertEqual(result["recommended_level"], 1)

    def test_no_level_passing_risk_ceiling_abstains(self):
        result = recommend([estimate(0, .2, .3, intrusion_upper=.4)],
                           eligible_levels={0}, max_intrusion_risk=.2,
                           evidence=VALID_EVIDENCE)
        self.assertEqual(result["status"], "risk_ceiling_exceeded")


if __name__ == "__main__":
    unittest.main()
