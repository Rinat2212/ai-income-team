"""Tests for deterministic DatingGrowth draft quality checks."""
import unittest

from projects.datinggrowth.quality_agent import check_outreach_text


class DatingGrowthQualityAgentTests(unittest.TestCase):
    def test_permission_request_passes(self):
        report = check_outreach_text(
            "Здравствуйте! Подскажите, пожалуйста, можно ли согласовать размещение? "
            "Готовы соблюдать правила сообщества."
        )
        self.assertTrue(report.approved_for_human_review)
        self.assertEqual(report.blockers, ())

    def test_mass_outreach_is_blocked(self):
        report = check_outreach_text("Планируем массовую рассылку всем участникам.")
        self.assertFalse(report.approved_for_human_review)
        self.assertTrue(report.blockers)

    def test_missing_permission_request_warns(self):
        report = check_outreach_text("Здравствуйте, посмотрите наш проект https://t.me/example")
        self.assertTrue(report.approved_for_human_review)
        self.assertTrue(any("разрешения" in warning for warning in report.warnings))

    def test_empty_and_oversized_text_blocked(self):
        self.assertFalse(check_outreach_text("").approved_for_human_review)
        self.assertFalse(check_outreach_text("x" * 3501).approved_for_human_review)


if __name__ == "__main__":
    unittest.main()
