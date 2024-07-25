import getpass
import pickle
import platform
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from git import Commit, Repo
from tqdm import tqdm

from . import __version__
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
                    "inquisitor_version": __version__,
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
                    "branch": self.repo.active_branch.name
                    or self.commit.hexsha + " (detached)",
                    "commit": {
                        "sha": self.commit.hexsha,
                        "date": self.commit.committed_datetime,
                        "tree": self.commit.tree.hexsha,
                        "contributor": f"{self.commit.committer.name} ({self.commit.committer.email})",
                        "message": self.commit.message,
                    },
                },
            },
            "contributors": {},
            "files": {},
            "history": [],
        }
        self._collect()
        self.report_adapter = report_adapter(self.data)

    def _collect(self) -> None:
        if self.cache_exists():
            self._load_data(self._get_cache_file())
        else:
            self._collect_blame_data_by_file()
            commits = list(self.repo.iter_commits("HEAD", reverse=True))
            for commit in tqdm(commits, desc="Processing Commits", leave=False):
                self._collect_commit_data(commit)
            self._collect_active_line_count_by_contributor()

    def _collect_active_line_count_by_contributor(self) -> None:
        for contributor in self.data["contributors"]:
            self.data["contributors"][contributor]["active_lines"] = sum(
                [
                    self.data["files"][file]["lines_by_contributor"].get(contributor, 0)
                    for file in self.data["files"]
                ]
            )

    def _collect_commit_data(self, commit: Commit) -> None:
        self._collect_commit_data_by_contributor(commit)
        self._collect_commit_history(commit)

    def _collect_commit_data_by_contributor(self, commit: Commit) -> None:
        contributor = commit.committer.name
        email = commit.committer.email
        if contributor not in self.data["contributors"]:
            self.data["contributors"][contributor] = {
                "identities": [email],
                "commit_count": 0,
                "insertions": 0,
                "deletions": 0,
                "active_lines": 0,
            }
        if email not in self.data["contributors"][contributor]["identities"]:
            self.data["contributors"][contributor]["identities"].append(email)

        self.data["contributors"][contributor]["commit_count"] += 1
        self.data["contributors"][contributor]["insertions"] += commit.stats.total[
            "insertions"
        ]
        self.data["contributors"][contributor]["deletions"] += commit.stats.total[
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
            if file_path not in self.data["files"]:
                self.data["files"][file_path] = self._get_blame_for_file(file_path)

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
            "top_contributor": (
                f"{top_contributor} ({lines_by_contributor.get(top_contributor, 0)/total_lines:.2%})"
                if total_lines
                else None
            ),
            "lines_by_contributor": lines_by_contributor,
        }

    def cache_data(self) -> None:
        if not self.cache_exists():
            self._save_data(self._get_cache_file())

    def _save_data(self, output_file: Path) -> None:
        data_bytes = pickle.dumps(self.data)
        if not output_file.parent.exists():
            output_file.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_file, "w") as zipf:
            zipf.writestr("data.pickle", data_bytes)

    def _load_data(self, input_file: Path) -> None:
        with zipfile.ZipFile(input_file, "r") as zipf:
            data_bytes = zipf.read("data.pickle")
        self.data = pickle.loads(data_bytes)

    def cache_exists(self) -> bool:
        return self._get_cache_file().exists()

    def _get_cache_file(self) -> Path:
        return (
            Path(self.repo_path)
            .joinpath(".inquisitor", "cache")
            .joinpath(self.commit.hexsha + ".zip")
        )

    def write_report(self, output_file: Path) -> None:
        self.report_adapter.write(output_file)
