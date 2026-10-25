"""Tests for permission-first outreach copy generation."""
import unittest

from projects.datinggrowth.content_agent import OutreachBrief, generate_admin_outreach, validate_brief


class ContentAgentTests(unittest.TestCase):
    def setUp(self):
        self.brief = OutreachBrief(
            community_name="Знакомства Москва",
            bot_name="@my_daivinchik_2212_bot",
            purpose="помогает пользователям знакомиться",
            public_link="https://t.me/my_daivinchik_2212_bot",
        )

    def test_generates_three_permission_first_variants(self):
        variants = generate_admin_outreach(self.brief)
        self.assertEqual(len(variants), 3)
        self.assertTrue(all("разреш" in text.lower() or "соглас" in text.lower() for text in variants))
        self.assertTrue(all(self.brief.public_link in text for text in variants))

    def test_rejects_missing_purpose(self):
        brief = OutreachBrief("Группа", "Бот", " ", "https://t.me/example_bot")
        with self.assertRaises(ValueError):
            validate_brief(brief)

    def test_rejects_non_telegram_link(self):
        brief = OutreachBrief("Группа", "Бот", "Описание", "https://example.com")
        with self.assertRaises(ValueError):
            validate_brief(brief)


if __name__ == "__main__":
    unittest.main()
