import sys
import platform
from pathlib import Path
from tqdm import tqdm
from git import Repo, Commit
from datetime import datetime
import getpass
from .report import JsonReportAdapter, ReportAdapter


class GitDataCollector:
    def __init__(
        self, repo_path: Path, report_adapter: ReportAdapter = JsonReportAdapter
    ) -> None:
        self.repo_path: Path = repo_path
        self.repo: Repo = Repo(repo_path)
        self.commit: Commit = self.repo.head.commit
        self.data = {
            "metadata": {
                "collector": {
                    "date_collected": datetime.now(),
                    "user": getpass.getuser(),
                    "hostname": platform.node(),
                    "platform": platform.platform(),
                    "python_version": f"{platform.python_version()} ({sys.executable})",
                    "git_version": ".".join(
                        [str(x) for x in self.repo.git.version_info]
                    ),
                },
                "repo": {
                    "url": self.repo.remotes.origin.url,
                    "branch": self.repo.active_branch.name,
                    "commit": {
                        "sha": self.commit.hexsha,
                        "date": self.commit.committed_datetime,
                        "tree": self.commit.tree.hexsha,
                        "contributor": f"{self.commit.committer.name} ({self.commit.committer.email})",
                        "message": self.commit.message,
                    },
                },
            },
            "by_contributor": {},
            "by_file": {},
            "history": [],
        }
        self._collect()
        self.report_adapter = report_adapter(self.data)

    def _collect(self) -> None:
        self._collect_blame_data_by_file()
        commits = list(self.repo.iter_commits("HEAD", reverse=True))
        for commit in tqdm(commits, desc="Processing Commits", leave=False):
            self._collect_commit_data(commit)
        self._collect_active_line_count_by_contributor()

    def _collect_active_line_count_by_contributor(self) -> None:
        for contributor in self.data["by_contributor"]:
            self.data["by_contributor"][contributor]["active_lines"] = sum(
                [
                    self.data["by_file"][file]["lines_by_contributor"].get(
                        contributor, 0
                    )
                    for file in self.data["by_file"]
                ]
            )

    def _collect_commit_data(self, commit: Commit) -> None:
        self._collect_commit_data_by_contributor(commit)
        self._collect_commit_history(commit)

    def _collect_commit_data_by_contributor(self, commit: Commit) -> None:
        contributor = commit.committer.name
        email = commit.committer.email
        if contributor not in self.data["by_contributor"]:
            self.data["by_contributor"][contributor] = {
                "identities": [email],
                "commit_count": 0,
                "insertions": 0,
                "deletions": 0,
                "active_lines": 0,
            }
        if email not in self.data["by_contributor"][contributor]["identities"]:
            self.data["by_contributor"][contributor]["identities"].append(email)

        self.data["by_contributor"][contributor]["commit_count"] += 1
        self.data["by_contributor"][contributor]["insertions"] += commit.stats.total[
            "insertions"
        ]
        self.data["by_contributor"][contributor]["deletions"] += commit.stats.total[
            "deletions"
        ]

    def _collect_commit_history(self, commit: Commit) -> None:
        _data = {
            "commit": commit.hexsha,
            "parents": [p.hexsha for p in commit.parents],
            "tree": commit.tree.hexsha,
            "contributor": f"{commit.committer.name} ({commit.committer.email})",
            "date": commit.committed_datetime,
            "message": commit.message,
            "insertions": commit.stats.total["insertions"],
            "deletions": commit.stats.total["deletions"],
            "files": commit.stats.files,
        }
        self.data["history"].append(_data)

    def _collect_blame_data_by_file(self) -> None:
        for file_path in tqdm(
            self.repo.git.ls_files().split("\n"), desc="Processing Files", leave=False
        ):
            if file_path not in self.data["by_file"]:
                self.data["by_file"][file_path] = self._get_blame_for_file(file_path)

    def _get_blame_for_file(self, file_path: Path) -> dict:
        lines_by_contributor = {}
        total_lines = 0
        total_commits = 0
        current_date = None
        current_contributor = None
        top_contributor = current_contributor
        for _blame in self.repo.blame_incremental(self.commit, file_path):
            _commit = _blame.commit
            _contributor = _commit.committer.name

            if not _blame.linenos:
                continue

            current_date = _blame.commit.committed_datetime
            current_contributor = _contributor
            total_commits += 1
            if _contributor not in lines_by_contributor:
                lines_by_contributor[_contributor] = 0
            for line_number in _blame.linenos:
                total_lines += 1
                lines_by_contributor[_contributor] += 1

            top_contributor = max(lines_by_contributor, key=lines_by_contributor.get)
            lines_by_contributor = dict(
                sorted(
                    lines_by_contributor.items(), key=lambda item: item[1], reverse=True
                )
            )

        return {
            "date_introduced": current_date,
            "original_author": current_contributor,
            "total_commits": total_commits,
            "total_lines": total_lines,
            "top_contributor": f"{top_contributor} ({lines_by_contributor.get(top_contributor, 0)/total_lines:.2%})"
            if total_lines
            else None,
            "lines_by_contributor": lines_by_contributor,
        }

    def write_report(self, output_file: Path) -> None:
        self.report_adapter.write(output_file)
