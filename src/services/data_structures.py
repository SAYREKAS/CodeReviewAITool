from enum import Enum

from pydantic import BaseModel


class Content(BaseModel):
    filename: str
    file_content: str


class RepoFilesResponse(BaseModel):
    files: list[Content]
    count: int


class ErrorResponse(BaseModel):
    detail: str


class CandidateLevel(Enum):
    junior = "junior"
    middle = "middle"
    senior = "senior"


class AnalysisReport(BaseModel):
    project_files: list[str]
    full_report: str
    conclusion_and_assessment: str
