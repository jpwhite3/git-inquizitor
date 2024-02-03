import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .chart import pie_chart, commit_graph, change_graph

TEMPLATES_DIR = Path(__file__).parent / "templates"


class ReportAdapter:
    def __init__(self, data: dict, **kwargs) -> None:
        self.raw_data = data
        self.report_data = None

    def prepare_data(self) -> None:
        pass

    def write(self, output_file: Path) -> None:
        self.prepare_data()
        with open(output_file, "w") as f:
            f.write(self.report_data)


class JsonReportAdapter(ReportAdapter):
    def prepare_data(self) -> None:
        self.report_data = json.dumps(self.raw_data, indent=4, default=str)


class HtmlReportAdapter(ReportAdapter):
    def prepare_data(self) -> None:
        self.raw_data["history"].sort(key=lambda x: x["date"], reverse=True)
        self.chart_data = {
            "commits_by_author": pie_chart(
                self.raw_data["by_contributor"].keys(),
                list(
                    map(
                        lambda x: x["commit_count"],
                        self.raw_data["by_contributor"].values(),
                    )
                ),
                title="Commits by Author",
            ),
            "changes_by_author": pie_chart(
                self.raw_data["by_contributor"].keys(),
                list(
                    map(
                        lambda x: x["insertions"] + x["deletions"],
                        self.raw_data["by_contributor"].values(),
                    )
                ),
                title="Line changes by Author",
            ),
            "commit_history_chart": commit_graph(self.raw_data["history"]),
            "change_history_chart": change_graph(self.raw_data["history"]),
        }
        env = Environment(
            loader=FileSystemLoader(
                TEMPLATES_DIR,
                encoding="utf8",
                followlinks=True,
            ),
        )
        env.add_extension("jinja2_humanize_extension.HumanizeExtension")
        template = env.get_template("html.template")
        self.report_data = template.render(
            data=self.raw_data, chart_data=self.chart_data
        )
