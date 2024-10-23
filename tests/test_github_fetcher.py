import pytest
from fastapi import HTTPException
from src.services.github_fetcher import get_repository_files
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_get_repository_files_invalid_url():
    """Test for invalid GitHub repository URL."""
    invalid_url = "https://invalid-url.com"

    with pytest.raises(HTTPException) as exc_info:
        await get_repository_files(invalid_url)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Failed to fetch repository files"


@pytest.mark.asyncio
async def test_get_repository_files_no_token():
    """Test for missing GitHub token."""
    with patch("os.getenv", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await get_repository_files("https://github.com/owner/repo")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Failed to fetch repository files"


@pytest.mark.asyncio
async def test_get_repository_files_failed_api_call():
    """Test GitHub API failure when retrieving files."""
    with patch("httpx.AsyncClient.get", AsyncMock(return_value=AsyncMock(status_code=500))):
        with pytest.raises(HTTPException) as exc_info:
            await get_repository_files("https://github.com/owner/repo")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Failed to fetch repository files"
