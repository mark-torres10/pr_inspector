"""Service for interacting with the GitHub API."""

from dataclasses import dataclass

from github import Github, Auth
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.Repository import Repository

from pr_inspector.env_loader import fetch_env_variable


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
        paginated_files: PaginatedList = pr.get_files()
        pr_files: list[PrFile] = self.create_pr_files(paginated_files)
        return PrDetails(
            org_name=org_name,
            repo_name=repo_name,
            pr_number=pr_number,
            pr_title=pr.title,
            pr_body=pr.body,
            pr_files=pr_files,
        )

    def create_pr_files(self, files: PaginatedList) -> list[PrFile]:
        """Given the paginated list of files from the Github API, create the
        internal representation of the files."""
        return [
            PrFile(file_name=file.filename, file_diff=file.patch)
            for file in files
            if file.patch is not None # can happen if file is binary or too large.
        ]


if __name__ == "__main__":
    example_pr_link = "https://github.com/METResearchGroup/bluesky-research/pull/273"
    github_service = GithubService()
    github_service.authenticate()
    pr_details: PrDetails = github_service.fetch_pr_details(example_pr_link)
    print(pr_details)
