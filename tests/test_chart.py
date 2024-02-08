import unittest
from datetime import datetime

from inquisitor.chart import change_graph


class TestChangeGraph(unittest.TestCase):
    def test_change_graph(self):
        # Mock the commits data
        commits = [
            {
                "date": datetime(2022, 1, 1),
                "insertions": 5,
                "deletions": 3,
            },
            {
                "date": datetime(2022, 1, 2),
                "insertions": 3,
                "deletions": 1,
            },
        ]

        # Call the change_graph function
        image_base64 = change_graph(commits)

        # Assert that the image is generated correctly
        self.assertIsInstance(image_base64, str)
        self.assertTrue(image_base64.startswith("iVBORw0KGgoAAAANSUhEUgAA"))

        # You can add more specific assertions based on your requirements


if __name__ == "__main__":
    unittest.main()
