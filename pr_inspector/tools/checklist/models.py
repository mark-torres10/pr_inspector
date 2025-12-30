from pydantic import BaseModel
from pydantic.json_schema import model_json_schema


class PerFileNote(BaseModel):
    file_name: str
    purpose: str
    critical_sections: list[str]
    pitfalls: list[str]
    dependencies: list[str]


class FileReviewOrder(BaseModel):
    """A file to review with its order and reasoning."""
    file_name: str
    order: int
    reason: str


class KeyFilesAndReviewOrder(BaseModel):
    """Key files to examine with specified order and reasoning."""
    files: list[FileReviewOrder]
    overall_approach: str  # Summary of why this order matters


class CrossCuttingConcern(BaseModel):
    """A cross-cutting concern that spans multiple files."""
    concern_type: str  # e.g., "error handling", "logging", "API contracts"
    description: str
    affected_files: list[str]  # Files where this concern applies
    consistency_notes: str  # Notes about ensuring consistency


class CrossCuttingConcerns(BaseModel):
    """Design patterns, abstractions, and conventions that span files."""
    concerns: list[CrossCuttingConcern]
    summary: str  # Overall summary of cross-cutting patterns


class RiskOrTradeoff(BaseModel):
    """A risk or tradeoff identified in the PR."""
    description: str
    category: str  # e.g., "security", "performance", "scalability", "maintainability", "fragile_area", "compromise"
    severity: str  # e.g., "low", "medium", "high"
    affected_areas: list[str]  # Files or components affected


class RisksAndTradeoffs(BaseModel):
    """Known fragile areas, compromises, and potential issues."""
    risks: list[RiskOrTradeoff]
    summary: str  # Overall summary of risks and tradeoffs


class Context(BaseModel):
    """Background assumptions, constraints, and conventions."""
    background_assumptions: list[str]
    constraints: list[str]
    design_decisions: list[str]
    style_conventions: list[str]  # Style/architectural conventions
    architectural_conventions: list[str]


class TestingAndValidation(BaseModel):
    """Testing and validation information for the PR review."""
    files_tests_covered: list[str]
    missing_scenarios: list[str]
    manual_checks: list[str]


class ChecklistOutput(BaseModel):
    """Output of the PR review checklist."""
    key_files_and_review_order: KeyFilesAndReviewOrder
    per_file_notes: list[PerFileNote]
    cross_cutting_concerns: CrossCuttingConcerns
    testing_and_validation: TestingAndValidation
    risks_and_tradeoffs: RisksAndTradeoffs
    context: Context
