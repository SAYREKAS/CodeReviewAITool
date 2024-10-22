from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_fetch_files_success():
    response = client.post(url="/files", json={"github_repo_url": "https://github.com/SAYREKAS/GymHelper"})
    assert response.status_code == 200
    assert "files" in response.json()
    assert "count" in response.json()


def test_fetch_files_not_found():
    response = client.post(url="/files", json={"github_repo_url": "https://github.com/SAYREKAS/randomqwrt"})
    assert response.status_code == 404


def test_review_success():
    response = client.post(
        url="/review", json={
            "assignment_description": "Analyze this code",
            "github_repo_url": "https://github.com/SAYREKAS/GymHelper",
            "candidate_level": "junior"
        }
    )
    assert response.status_code == 200
    assert "project_files" in response.json()
    assert "full_report" in response.json()
    assert "conclusion_and_assessment" in response.json()


def test_review_no_files():
    response = client.post(
        url="/review", json={
            "assignment_description": "Analyze this code",
            "github_repo_url": "https://github.com/SAYREKAS/randomqwrt",
            "candidate_level": "junior"
        }
    )
    assert response.status_code == 404


def test_review_missing_fields():
    response = client.post(
        url="/review", json={
            "github_repo_url": "https://github.com/SAYREKAS/GymHelper",
            "candidate_level": "junior"
        }
    )
    assert response.status_code == 422


def test_review_invalid_candidate_level():
    response = client.post(
        url="/review", json={
            "assignment_description": "Analyze this code",
            "github_repo_url": "https://github.com/SAYREKAS/GymHelper",
            "candidate_level": "invalid_level"
        }
    )
    assert response.status_code == 422


def test_review_empty_request_body():
    response = client.post(url="/review", json={})
    assert response.status_code == 422
