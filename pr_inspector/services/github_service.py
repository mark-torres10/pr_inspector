"""Service for interacting with the GitHub API."""

import logging
import threading
from dataclasses import dataclass

from github import Github, Auth
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.Repository import Repository

from pr_inspector.env_loader import fetch_env_variable

logger = logging.getLogger(__name__)

MAX_DIFF_LENGTH = 1000


@dataclass
class PrFile:
    file_name: str
    file_diff: str

@dataclass
class PrDetails:
    org_name: str
    repo_name: str
    pr_number: int
    pr_title: str
    pr_body: str
    pr_files: list[PrFile]

    def __str__(self) -> str:
        output = []
        output.append("=== PR Info ===")
        output.append(f"Title: {self.pr_title}\n")
        output.append(f"Body: {self.pr_body.strip() if self.pr_body else ''}\n")
        output.append("\n=== Files Changed ===")
        for pr_file in self.pr_files:
            output.append(f"- {pr_file.file_name}:")
            # TODO: see if we should truncate or not. Currently truncating
            # for testing urposes, might change later.
            if pr_file.file_diff is not None:
                diff_snippet = pr_file.file_diff[:MAX_DIFF_LENGTH]
                # add ellipsis if truncated
                if len(pr_file.file_diff) > MAX_DIFF_LENGTH:
                    logger.info(f"Diff for {pr_file.file_name} was truncated to {MAX_DIFF_LENGTH} characters.")
                    diff_snippet += " ..."
                output.append(f"  Diff Start: {diff_snippet}")
            else:
                output.append("  (No diff available)")
        return "\n".join(output)

class GithubService:
    """GitHub service for fetching PR details."""
    def __init__(self):
        self.github_token = fetch_env_variable("GITHUB_TOKEN")
        self.github_client = None

    def authenticate(self):
        if self.github_client is None:
            self.github_client = Github(auth=Auth.Token(self.github_token))

    def fetch_pr_details(self, pr_link: str):
        split_pr_link: list[str] = pr_link.split("/")
        org_name: str = split_pr_link[3]
        repo_name: str = split_pr_link[4]
        pr_number: int = int(split_pr_link[-1])
        print(f"""
        Org name: {org_name}, 
        Repo name: {repo_name}, 
        PR number: {pr_number}
        """)
        repo: Repository = self.github_client.get_repo(f"{org_name}/{repo_name}")
        pr: PullRequest = repo.get_pull(pr_number)
        pr_files: list[PrFile] = self.get_pr_files(pr)
        return PrDetails(
            org_name=org_name,
            repo_name=repo_name,
            pr_number=pr_number,
            pr_title=pr.title,
            pr_body=pr.body,
            pr_files=pr_files,
        )

    def get_pr_files(self, pr: PullRequest) -> list[PrFile]:
        """Given the paginated list of files from the Github API, create the
        internal representation of the files."""
        paginated_files: PaginatedList = pr.get_files()
        return [
            PrFile(file_name=file.filename, file_diff=file.patch)
            for file in paginated_files
            if file.patch is not None # can happen if file is binary or too large.
        ]


# Provider function for dependency injection
_github_service_instance: GithubService | None = None
_github_service_lock = threading.Lock()


def get_github_service() -> GithubService:
    """Dependency provider for GitHub service."""
    global _github_service_instance
    if _github_service_instance is None:
        with _github_service_lock:
            if _github_service_instance is None:
                _github_service_instance = GithubService()
                _github_service_instance.authenticate()
    return _github_service_instance


if __name__ == "__main__":
    example_pr_link = "https://github.com/METResearchGroup/bluesky-research/pull/273"
    github_service = GithubService()
    github_service.authenticate()
    pr_details: PrDetails = github_service.fetch_pr_details(example_pr_link)
    print(pr_details)
