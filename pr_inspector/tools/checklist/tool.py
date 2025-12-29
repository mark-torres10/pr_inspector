"""Tool for creating PR review checklists."""

from fastmcp.dependencies import Depends

from pr_inspector.mcp_instance import mcp
from pr_inspector.services.github_service import (
    GithubService,
    get_github_service,
    PrDetails,
)
from pr_inspector.services.openai_service import (
    OpenAIService,
    get_openai_service,
)

prompt = """

You are an expert code reviewer. You are given details of a Github pull request.

You are to generate a checklist of items that should be reviewed for the pull request.

The checklist should following the following format:

{checklist_template}

The details of the pull request are as follows:

{pr_details}

Please generate a checklist of items that should be reviewed for the pull request.

"""

checklist_template = """
- [ ] **Key Files & Review Order**  
  - List the key files to examine.  
  - Specify the order and why it matters.  
  - *Example:* “Start with `config.py` (sets constants), then `database.py` (schema), then `api.py` (uses both).”

- [ ] **Per-File Notes**  
  For each file, provide:  
  - [ ] Purpose and role in the system.  
    - *Example:* “`handlers.py` manages HTTP routes → business logic.”  
  - [ ] Critical sections to inspect (functions, classes, blocks).  
    - *Example:* “Check `UserManager.create_user()` — touches DB, hashing, validation.”  
  - [ ] Pitfalls or tricky logic.  
    - *Example:* “Pagination in `query_posts()` — check for off-by-one errors.”  
  - [ ] Dependencies or external assumptions.  
    - *Example:* “Assumes Redis always available — no retry logic.”

- [ ] **Cross-Cutting Concerns**  
  - Highlight design patterns, abstractions, or conventions that span files.  
  - Call out areas needing consistency (e.g., error handling, logging, API contracts).  
  - *Example:* “Ensure `api.py` and `tasks.py` return errors in the same JSON format.”

- [ ] **Testing & Validation**  
  - [ ] Which files contain tests and what's covered.  
  - [ ] What scenarios or edge cases are missing.  
  - [ ] Suggested manual or integration checks.  
  - *Example:* “`test_models.py` covers user creation, but missing duplicate email case.”  
  - *Example:* “Manually test concurrent writes to `update_balance()` for race conditions.”

- [ ] **Risks & Tradeoffs**  
  - [ ] Known fragile areas or compromises.  
  - [ ] Potential security, performance, scalability, or maintainability issues.  
  - *Example:* “Blocking DB calls may cause performance issues under load.”  
  - *Example:* “Password hashing with SHA256 instead of bcrypt — security risk.”

- [ ] **Context**  
  - [ ] Background assumptions, constraints, or design decisions.  
  - [ ] Style/architectural conventions to keep in mind.  
  - *Example:* “Using SQLite now, but schema designed for Postgres compatibility.”  
  - *Example:* “PEP8 + Google docstrings are expected.”
"""

def generate_prompt(pr_details: PrDetails) -> str:
    breakpoint()
    return prompt.format(checklist_template=checklist_template, pr_details=pr_details)


def _create_pr_checklist_impl(
    pr_url: str,
    github_service: GithubService,
    openai_service: OpenAIService,
) -> str:
    """
    Creates a comprehensive code review checklist customized for a specific GitHub PR.
    
    Fetches PR details from GitHub API and generates a markdown checklist with:
    - Pre-filled list of files changed in the PR
    - PR context (title, description, branches)
    - Template sections for review notes
    
    Args:
        pr_url: Full GitHub PR URL (e.g., "https://github.com/owner/repo/pull/123")
        github_service: Injected GitHub service (not part of MCP signature)
        openai_service: Injected OpenAI service (not part of MCP signature)
    
    Returns:
        Markdown-formatted checklist string, or error message if fetch fails
    """
    pr_details: PrDetails = github_service.fetch_pr_details(pr_url)
    prompt: str = generate_prompt(pr_details)
    return f"Checklist for PR: {pr_url}"


@mcp.tool()
def create_pr_checklist(
    pr_url: str,
    github_service: GithubService = Depends(get_github_service),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> str:
    """Generate a comprehensive code review checklist for a specific GitHub PR."""
    return _create_pr_checklist_impl(pr_url, github_service, openai_service)

if __name__ == "__main__":
    pr_url = "https://github.com/METResearchGroup/bluesky-research/pull/273"
    _create_pr_checklist_impl(pr_url, get_github_service(), get_openai_service())
