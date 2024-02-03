from pathlib import Path
from .collector import GitDataCollector
from git.exc import GitCommandError
from .report import HtmlReportAdapter

repo_path = Path("/Users/jpwhite/Code/lvlup/aws-serverless-registration-app")
json_output_file = Path("git_statistics.json")
html_output_file = Path("git_statistics.html")

try:
    collector = GitDataCollector(repo_path)
    collector.write_report(json_output_file)
    collector.report_adapter = HtmlReportAdapter(collector.data)
    collector.write_report(html_output_file)
except GitCommandError as e:
    print(f"Error: {e}")
