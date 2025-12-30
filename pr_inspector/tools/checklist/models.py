from pydantic import BaseModel
from pydantic.json_schema import model_json_schema


class PerFileNote(BaseModel):
    file_name: str
    purpose: str
    critical_sections: list[str]
    pitfalls: list[str]
    dependencies: list[str]

class ChecklistOutput(BaseModel):
    key_files_and_review_order: str
    per_file_notes: list[PerFileNote]
    cross_cutting_concerns: str
    testing_and_validation: dict
    risks_and_tradeoffs: list[str]
    context: str
