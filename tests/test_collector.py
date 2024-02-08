import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from inquisitor.collector import GitDataCollector


class TestGitDataCollector(unittest.TestCase):
    def setUp(self):
        self.repo_path = Path(__file__).parent.parent
        self.collector = GitDataCollector(self.repo_path)

    def test_init(self):
        self.assertEqual(self.collector.repo_path, self.repo_path)
        self.assertIsInstance(self.collector.repo, MagicMock)
        self.assertIsInstance(self.collector.commit, MagicMock)
        self.assertIsInstance(self.collector.data, dict)
        self.assertIsInstance(self.collector.report_adapter, MagicMock)

    def test_collect_active_line_count_by_contributor(self):
        # Mock the data
        self.collector.data = {
            "contributors": {
                "contributor1": {"active_lines": 10},
                "contributor2": {"active_lines": 20},
            },
            "files": {
                "file1": {"lines_by_contributor": {"contributor1": 5}},
                "file2": {"lines_by_contributor": {"contributor2": 10}},
            },
        }

        # Call the method
        self.collector._collect_active_line_count_by_contributor()

        # Check the result
        self.assertEqual(
            self.collector.data["contributors"]["contributor1"]["active_lines"], 5
        )
        self.assertEqual(
            self.collector.data["contributors"]["contributor2"]["active_lines"], 10
        )

    def test_collect_commit_data_by_contributor(self):
        # Mock the data
        commit = MagicMock()
        commit.committer.name = "contributor1"
        commit.committer.email = "contributor1@example.com"
        commit.stats.total = {"insertions": 5, "deletions": 3}

        # Call the method
        self.collector._collect_commit_data_by_contributor(commit)

        # Check the result
        self.assertEqual(
            self.collector.data["contributors"]["contributor1"]["commit_count"], 1
        )
        self.assertEqual(
            self.collector.data["contributors"]["contributor1"]["insertions"], 5
        )
        self.assertEqual(
            self.collector.data["contributors"]["contributor1"]["deletions"], 3
        )

    def test_collect_commit_history(self):
        # Mock the data
        commit = MagicMock()
        commit.hexsha = "123456"
        commit.parents = []
        commit.tree.hexsha = "abcdef"
        commit.committer.name = "contributor1"
        commit.committer.email = "contributor1@example.com"
        commit.committed_datetime = datetime(2022, 1, 1)
        commit.message = "Commit message"
        commit.stats.total = {"insertions": 5, "deletions": 3}
        commit.stats.files = {"file1": 2, "file2": 3}

        # Call the method
        self.collector._collect_commit_history(commit)

        # Check the result
        self.assertEqual(len(self.collector.data["history"]), 1)
        self.assertEqual(self.collector.data["history"][0]["commit"], "123456")
        self.assertEqual(self.collector.data["history"][0]["parents"], [])
        self.assertEqual(self.collector.data["history"][0]["tree"], "abcdef")
        self.assertEqual(
            self.collector.data["history"][0]["contributor"],
            "contributor1 (contributor1@example.com)",
        )
        self.assertEqual(
            self.collector.data["history"][0]["date"], datetime(2022, 1, 1)
        )
        self.assertEqual(self.collector.data["history"][0]["message"], "Commit message")
        self.assertEqual(self.collector.data["history"][0]["insertions"], 5)
        self.assertEqual(self.collector.data["history"][0]["deletions"], 3)
        self.assertEqual(
            self.collector.data["history"][0]["files"], {"file1": 2, "file2": 3}
        )

    # Add more test methods for other methods in the GitDataCollector class


if __name__ == "__main__":
    unittest.main()
