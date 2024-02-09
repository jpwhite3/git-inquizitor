import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from git_inquisitor.report import ReportAdapter


class TestReportAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ReportAdapter({})

    def test_prepare_data(self):
        # Mock the raw data
        self.adapter.raw_data = {
            # Add your test data here
        }

        # Call the prepare_data method
        self.adapter.prepare_data()

        # Add your assertions here

    @patch("git_inquisitor.report.Path")
    def test_write(self, mock_path):
        # Mock the raw data
        self.adapter.raw_data = {
            # Add your test data here
        }

        # Set up a mock output file path
        output_file = MagicMock(spec=Path)
        mock_path.return_value = output_file

        # Call the write method
        with patch("git_inquisitor.report.ReportAdapter.write") as mock_write:
            self.adapter.write(output_file)
            mock_write.assert_called_once_with(output_file)

        # Add your assertions here


if __name__ == "__main__":
    unittest.main()
