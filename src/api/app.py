from uvicorn import run
from fastapi import FastAPI

from src.services.data_structures import CandidateLevel
from src.services.github_fetcher import get_repository_files
from src.services.gpt_code_analyzer import GPTCandidateAnalyzer

app = FastAPI()


@app.post("/review")
def review(assignment_description: str, github_repo_url: str, candidate_level: CandidateLevel):
    files = get_repository_files(github_repo_url)
    if files is None:
        return {"message": "No repository files found"}

    analyzer = GPTCandidateAnalyzer(
        file_contents=files,
        candidate_level=candidate_level,
        assignment_description=assignment_description
    )
    return analyzer.analysis_report


if __name__ == '__main__':
    run(app="main:app", reload=True)
