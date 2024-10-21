from uvicorn import run
from fastapi import FastAPI, HTTPException

from src.services.data_structures import CandidateLevel, RepoFilesResponse, ErrorResponse, AnalysisReport
from src.services.github_fetcher import get_repository_files
from src.services.gpt_code_analyzer import GPTCandidateAnalyzer

app = FastAPI()


@app.post(
    path="/files",
    tags=["GitHub"],
    response_model=RepoFilesResponse,
    responses={404: {"model": ErrorResponse}},
)
def fetch_files_from_the_specified_repository(github_repo_url: str):
    return get_repository_files(github_repo_url)


@app.post(
    path="/review",
    tags=["Code review AI tool"],
    response_model=AnalysisReport,
)
def review(assignment_description: str, github_repo_url: str, candidate_level: CandidateLevel) -> AnalysisReport:
    file_contents = get_repository_files(github_repo_url)
    if not file_contents:
        raise HTTPException(status_code=404, detail="No repository files found")

    result = GPTCandidateAnalyzer(
        file_contents=file_contents,
        candidate_level=candidate_level,
        assignment_description=assignment_description
    )
    return result.analysis_report


if __name__ == '__main__':
    run(app="src.api.app:app", reload=True)
