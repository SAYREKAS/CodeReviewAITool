from uvicorn import run
from fastapi import FastAPI, HTTPException

from src.services.data_structures import RepoFilesResponse, ErrorResponse, AnalysisReport, ReviewRequest, FilesRequest
from src.services.github_fetcher import get_repository_files
from src.services.gpt_code_analyzer import GPTCandidateAnalyzer

app = FastAPI()


@app.post(
    path="/files",
    tags=["GitHub"],
    response_model=RepoFilesResponse,
    responses={404: {"model": ErrorResponse}},
)
def fetch_files_from_the_specified_repository(request: FilesRequest):
    return get_repository_files(request.github_repo_url)


@app.post(
    path="/review",
    tags=["Code review AI tool"],
    response_model=AnalysisReport,
    responses={404: {"model": ErrorResponse}},
)
def review(request: ReviewRequest) -> AnalysisReport:
    file_contents = get_repository_files(request.github_repo_url)
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
