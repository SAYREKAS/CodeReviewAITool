from uvicorn import run
from fastapi import FastAPI, HTTPException

from src.services.github_fetcher import get_repository_files
from src.services.gpt_code_analyzer import GPTCandidateAnalyzer
from src.services.data_structures import RepoFilesResponse, ErrorResponse, AnalysisReport, ReviewRequest, FilesRequest

app = FastAPI()


@app.post(
    path="/files",
    tags=["GitHub"],
    response_model=RepoFilesResponse,
    responses={404: {"model": ErrorResponse}},
)
async def fetch_files_from_the_specified_repository(request: FilesRequest) -> RepoFilesResponse:
    """
    Fetch files from the specified GitHub repository.

    Args:
        request (FilesRequest): The request object containing the GitHub repository URL.

    Returns:
        RepoFilesResponse: A response containing the retrieved files and their count.

    Raises:
        HTTPException: If the repository URL is invalid or no files are found.
    """
    return await get_repository_files(request.github_repo_url)


@app.post(
    path="/review",
    tags=["Code review AI tool"],
    response_model=AnalysisReport,
    responses={404: {"model": ErrorResponse}},
)
async def review(request: ReviewRequest) -> AnalysisReport:
    """
    Perform code review analysis on the specified GitHub repository.

    Args:
        request (ReviewRequest): The request object containing the assignment description,
                                 GitHub repository URL, and candidate level.

    Returns:
        AnalysisReport: The structured analysis report generated from the code review.

    Raises:
        HTTPException: If no repository files are found or other errors occur during analysis.
    """
    file_contents = await get_repository_files(request.github_repo_url)
    if not file_contents:
        raise HTTPException(status_code=404, detail="No repository files found")

    result = GPTCandidateAnalyzer(
        file_contents=file_contents,
        candidate_level=request.candidate_level,
        assignment_description=request.assignment_description
    )
    return result.analysis_report


if __name__ == '__main__':
    run(app="src.api.app:app", reload=True)
