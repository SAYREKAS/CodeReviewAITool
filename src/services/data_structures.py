from enum import Enum
from pydantic import BaseModel


class Content(BaseModel):
    """
    Represents the content of a file in a GitHub repository.

    Attributes:
        filename (str): The name of the file.
        file_content (str): The content of the file as a string.
    """
    filename: str
    file_content: str


class RepoFilesResponse(BaseModel):
    """
    Represents the response containing files retrieved from a GitHub repository.

    Attributes:
        files (list[Content]): A list of Content objects representing the files.
        count (int): The total number of files retrieved.
    """
    files: list[Content]
    count: int


class ErrorResponse(BaseModel):
    """
    Represents an error response.

    Attributes:
        detail (str): A description of the error.
    """
    detail: str


class CandidateLevel(Enum):
    """
    Enumeration for candidate levels.

    Values:
        junior: Represents a junior level candidate.
        middle: Represents a middle level candidate.
        senior: Represents a senior level candidate.
    """
    junior = "junior"
    middle = "middle"
    senior = "senior"


class AnalysisReport(BaseModel):
    """
    Represents the analysis report generated from the code review.

    Attributes:
        project_files (list[str]): A list of filenames involved in the analysis.
        full_report (str): A detailed report of the analysis.
        conclusion_and_assessment (str): The final assessment and conclusion of the review.
    """
    project_files: list[str]
    full_report: str
    conclusion_and_assessment: str


class ReviewRequest(BaseModel):
    """
    Represents a request for code review analysis.

    Attributes:
        assignment_description (str): Description of the assignment to be analyzed.
        github_repo_url (str): The URL of the GitHub repository to analyze.
        candidate_level (CandidateLevel): The level of the candidate being evaluated.
    """
    assignment_description: str
    github_repo_url: str
    candidate_level: CandidateLevel


class FilesRequest(BaseModel):
    """
    Represents a request for files from a GitHub repository.

    Attributes:
        github_repo_url (str): The URL of the GitHub repository.
    """
    github_repo_url: str
