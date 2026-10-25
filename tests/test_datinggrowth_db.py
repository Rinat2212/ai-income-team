"""Tests for the DatingGrowth AI SQLite workflow (stdlib unittest)."""
import os
import tempfile
import unittest
from pathlib import Path

_TEMP = tempfile.TemporaryDirectory()
os.environ["DATINGGROWTH_DB"] = str(Path(_TEMP.name) / "test.sqlite3")

from projects.datinggrowth import db  # noqa: E402


class DatingGrowthDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()

    def test_community_and_draft_review_lifecycle(self):
        url = "https://t.me/example_public_group"
        cid = db.add_community("Example group", url, "Rules checked")
        self.assertTrue(any(row["id"] == cid for row in db.list_communities()))
        did = db.add_draft(cid, "A respectful proposal to the group admin.")
        self.assertEqual(db.list_drafts("pending")[0]["id"], did)
        self.assertTrue(db.review_draft(did, "approved"))
        self.assertFalse(db.review_draft(did, "rejected"))
        self.assertEqual(db.list_drafts("approved")[0]["status"], "approved")

    def test_invalid_decision_is_rejected(self):
        with self.assertRaises(ValueError):
            db.review_draft(1, "sent")

    def test_events_are_counted(self):
        before = db.stats()["tracked_starts"]
        db.record_event("campaign_alpha")
        self.assertEqual(db.stats()["tracked_starts"], before + 1)


if __name__ == "__main__":
    unittest.main()
