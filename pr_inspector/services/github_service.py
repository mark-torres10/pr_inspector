"""Service for interacting with the GitHub API."""

from dataclasses import dataclass

from github import Github, Auth

from pr_inspector.env_loader import fetch_env_variable


@dataclass
class PrDetails:
    org_name: str
    repo_name: str
    pr_number: int
    pr_title: str
    pr_body: str

class GithubService:
    """GitHub service for fetching PR details."""
    def __init__(self):
        github_token = fetch_env_variable("GITHUB_TOKEN")
        self.github_client = Github(auth=Auth.Token(github_token))

    def authenticate(self):
        pass

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
        repo = self.github_client.get_repo(f"{org_name}/{repo_name}")
        pr = repo.get_pull(pr_number)
        return PrDetails(
            org_name=org_name,
            repo_name=repo_name,
            pr_number=pr_number,
            pr_title=pr.title,
            pr_body=pr.body,
        )


if __name__ == "__main__":
    example_pr_link = "https://github.com/METResearchGroup/bluesky-research/pull/273"
    github_service = GithubService()
    pr_details: PrDetails = github_service.fetch_pr_details(example_pr_link)
    print(pr_details)
