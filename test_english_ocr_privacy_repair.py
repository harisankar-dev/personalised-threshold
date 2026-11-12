"""Targeted privacy-language repair; examples test software rules, not consumers."""
import unittest

from intrusive_ad_model import classify


class PrivacyCueRepairTests(unittest.TestCase):
    @staticmethod
    def cues(text):
        return {row["cue"] for row in classify(text)["evidence"]}

    def test_known_location_diagnostic(self):
        result = classify("We know where you live. Time starts now.")
        self.assertIn("precise_location", self.cues("We know where you live. Time starts now."))
        self.assertEqual(result["tier"], "high_intrusive")
        self.assertEqual(result["score_out_of_10"], 6)

    def test_fresh_explicit_activity_claims(self):
        self.assertIn("browsing_history", self.cues("We know what you searched for yesterday."))
        self.assertIn("explicit_surveillance", self.cues("We've tracked your activity across our site."))
        self.assertIn("direct_identifier", self.cues("We know your home address."))

    def test_exact_location_and_tracking_variants(self):
        self.assertIn("precise_location", self.cues("We know your exact location."))
        self.assertIn("explicit_surveillance", self.cues("We track your browsing history."))
        self.assertFalse(self.cues("We do not track your browsing history."))

    def test_five_level_creatives(self):
        ads = [
            'Big Shoe Sale! Get 30% Off This Weekend.',
            'Looking for Running Shoes? Explore Our Latest Collection.',
            'Still Thinking About Those Running Shoes You Searched for Yesterday?',
            'You Bought Running Shoes Six Months Ago. Time for Another Pair?',
            'We Know You Searched for Running Shoes Last Night, Bought a Pair Six Months Ago, and Usually Run Near Miramar Beach. Your New Shoes Are Waiting!',
        ]
        self.assertFalse(self.cues(ads[0]))
        self.assertFalse(self.cues(ads[1]))
        self.assertIn('browsing_history', self.cues(ads[2]))
        self.assertIn('purchase_history', self.cues(ads[3]))
        self.assertTrue({'browsing_history', 'purchase_history', 'approximate_location', 'combined_signals'} <= self.cues(ads[4]))
        self.assertNotIn('approximate_location', self.cues('Our shop is near Miramar Beach.'))
        self.assertNotIn('approximate_location', self.cues('We usually run near Miramar Beach.'))

    def test_private_offline_activity_claims(self):
        ad = "We know you checked your skin in the mirror this morning. We know you searched for ways to control your oily skin. And we know you've been ignoring sun protection despite spending hours outdoors. Sounds creepy? Maybe. But your skin deserves better."
        result = classify(ad)
        self.assertEqual(result['tier'], 'high_intrusive')
        self.assertIn('private_activity_claim', self.cues(ad))
        for text in ['We observed you spending time outdoors.', 'We know you visited the clinic yesterday.']:
            self.assertIn('private_activity_claim', self.cues(text))
        for text in ['Check your skin in the mirror each morning.', 'Enjoy spending time outdoors.', 'We know you want better sun protection.', "The phrase 'we know you checked the mirror' is misleading.", 'We do not know you checked your skin in the mirror.']:
            self.assertNotIn('private_activity_claim', self.cues(text))

    def test_promotion_pressure_without_private_knowledge(self):
        result = classify("STOP SCROLLING! Your skin deserves better! Don't let oily skin, sweat, and harsh sunlight ruin your day. Get instant confidence with our revolutionary sunscreen! Limited-time offer — BUY NOW before it's too late! Your skin won't wait, so why should you?")
        self.assertEqual(result['privacy_score'], 0)
        self.assertEqual({e['cue'] for e in result['evidence']}, {'attention_demand', 'urgent_call_to_action'})
        self.assertFalse(self.cues('A sunscreen for oily skin. Explore the collection.'))

    def test_ordinary_seller_and_form_language(self):
        ordinary = [
            "Visit our store.",
            "Our address is 10 King Street.",
            "Contact our support team at help@example.com.",
            "Enter your phone number to register.",
        ]
        for text in ordinary:
            with self.subTest(text=text):
                self.assertFalse(self.cues(text) & {
                    "precise_location", "explicit_surveillance", "browsing_history", "direct_identifier"})

    def test_negation_quotation_and_example_context(self):
        guarded = [
            "We do not know where you live.",
            "The campaign quoted 'We know where you live' as a bad example.",
            "For example, do not say 'We know what you searched for.'",
            "The phrase 'We've tracked your activity' is misleading.",
        ]
        for text in guarded:
            with self.subTest(text=text):
                self.assertFalse(self.cues(text) & {
                    "precise_location", "explicit_surveillance", "browsing_history"})


if __name__ == "__main__":
    unittest.main()
