import unittest

from core.coordinator import Coordinator


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.coordinator = Coordinator(["researcher", "content"])

    def test_agent_count(self):
        self.assertEqual(self.coordinator.status()["agents_total"], 2)

    def test_safe_mode(self):
        self.assertEqual(self.coordinator.status()["mode"], "DRY_RUN")

    def test_create_task(self):
        task = self.coordinator.create_task("Find a niche")
        self.assertEqual(task.name, "Find a niche")
        self.assertEqual(task.status, "pending")

    def test_empty_task_rejected(self):
        with self.assertRaises(ValueError):
            self.coordinator.create_task("   ")


if __name__ == "__main__":
    unittest.main()
