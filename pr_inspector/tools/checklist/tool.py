"""Tool for creating PR review checklists."""

import json

from fastmcp.dependencies import Depends
from openai.types.chat import ChatCompletion

from pr_inspector.mcp_instance import mcp
from pr_inspector.services.github_service import (
    GithubService,
    get_github_service,
    PrDetails,
)
from pr_inspector.services.openai_service import (
    OpenAIService,
    get_openai_service,
    DEFAULT_MODEL,
)
from pr_inspector.tools.checklist.models import ChecklistOutput
from pr_inspector.tools.checklist.prompt import checklist_prompt_template, checklist_template


def generate_prompt(pr_details: PrDetails) -> str:
    """Generate the prompt by formatting the template with checklist template and PR details."""
    pr_details_str = str(pr_details)
    return checklist_prompt_template.format(
        checklist_template=checklist_template,
        pr_details=pr_details_str
    )


def generate_response(
  prompt: str,
  openai_service: OpenAIService,
  model: str | None,
  output_schema: dict
) -> ChecklistOutput:
    if model is None:
        model = DEFAULT_MODEL

    response: ChatCompletion = openai_service.chat_completion(
      messages=[{"role": "user", "content": prompt}],
      model=model,
      response_format={
          "type": "json_schema",
          "json_schema": {
              "name": "checklist_output",
              "strict": True,  # Enforces strict schema compliance
              "schema": output_schema
          }
      }
    )
    content: str = response.choices[0].message.content
    json_data = json.loads(content)
    return ChecklistOutput(**json_data)


def transform_response_to_markdown(response: ChecklistOutput) -> str:
    markdown = f"# Checklist for PR:\n\n"
    markdown += f"## Key Files & Review Order\n\n"
    markdown += f"{response.key_files_and_review_order}\n\n"
    markdown += f"## Per-File Notes\n\n"
    for per_file_note in response.per_file_notes:
        markdown += f"- {per_file_note.file_name}\n"
        markdown += f"  - Purpose: {per_file_note.purpose}\n"
        markdown += f"  - Critical sections: {per_file_note.critical_sections}\n"
        markdown += f"  - Pitfalls: {per_file_note.pitfalls}\n"
        markdown += f"  - Dependencies: {per_file_note.dependencies}\n"
        markdown += f"\n"
    markdown += f"## Cross-Cutting Concerns\n\n"
    markdown += f"{response.cross_cutting_concerns}\n\n"
    markdown += f"## Testing & Validation\n\n"
    markdown += f"{response.testing_and_validation}\n\n"
    markdown += f"## Risks & Tradeoffs\n\n"
    markdown += f"{response.risks_and_tradeoffs}\n\n"
    markdown += f"## Context\n\n"
    markdown += f"{response.context}\n\n"
    return markdown


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
    output: ChecklistOutput = generate_response(
        prompt=prompt,
        openai_service=openai_service,
        model=DEFAULT_MODEL,
        output_schema=ChecklistOutput.model_json_schema()
    )
    return transform_response_to_markdown(output)


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
    markdown_response = _create_pr_checklist_impl(pr_url, get_github_service(), get_openai_service())
    print(markdown_response)
    breakpoint()
