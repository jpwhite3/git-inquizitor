import click
from pathlib import Path
from .collector import GitDataCollector
from git.exc import GitCommandError
from .report import HtmlReportAdapter, JsonReportAdapter


@click.group()
def inquisitor():
    pass


@inquisitor.command()
@click.argument("repo-path", type=click.Path(exists=True))
def collect(repo_path):
    collector = GitDataCollector(repo_path)
    collector.cache_data()


@inquisitor.command()
@click.argument("repo-path", type=click.Path(exists=True))
@click.argument("report-format", type=click.Choice(["html", "json"]))
@click.option("--output-file-path", "-o", default=None, help="Output file path")
def report(repo_path, report_format, output_file_path):
    if output_file_path is None:
        output_file_path = f"inquisitor-report.{report_format}"

    collector = GitDataCollector(repo_path)

    try:
        if report_format == "html":
            collector.report_adapter = HtmlReportAdapter(collector.data)
        elif report_format == "json":
            collector.report_adapter = JsonReportAdapter(collector.data)

        collector.write_report(Path(output_file_path))
    except GitCommandError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    inquisitor()
