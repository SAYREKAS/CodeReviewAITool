import pytest
from unittest.mock import patch
from fastapi import HTTPException
from src.services.github_fetcher import get_repository_files


# Тест на успішне отримання файлів із репозиторію
@patch("src.services.github_fetcher.g.get_repo")
def test_get_repository_files_success(mock_get_repo):
    mock_file = type(
        'FileContent', (object,),
        {'type': 'file', 'name': 'test_file.py', 'path': 'test_file.py',
         'decoded_content': b'print("Hello, world!")'}
    )
    mock_dir = type('DirContent', (object,), {'type': 'dir', 'name': 'test_dir', 'path': 'test_dir'})
    mock_get_repo.return_value.get_contents.return_value = [mock_file, mock_dir]

    result = get_repository_files("https://github.com/test_user/test_repo")

    assert result.count == 101
    assert result.files[0].filename == "test_file.py"
    assert "print" in result.files[0].file_content


# Тест на неправильний URL (без власника або репозиторію)
def test_get_repository_files_invalid_url():
    with pytest.raises(HTTPException) as excinfo:
        get_repository_files("https://invalid_url.com/test_user/test_repo")

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Failed to fetch repository files"


# Тест на випадок відсутності файлів у репозиторії
@patch("src.services.github_fetcher.g.get_repo")
def test_get_repository_files_no_files(mock_get_repo):
    mock_get_repo.return_value.get_contents.return_value = []
    result = get_repository_files("https://github.com/test_user/empty_repo")

    assert result.count == 0
    assert result.files == []


# Тест на помилку доступу до репозиторію
@patch("src.services.github_fetcher.g.get_repo")
def test_get_repository_files_repo_not_found(mock_get_repo):
    mock_get_repo.side_effect = Exception("Not Found")
    with pytest.raises(HTTPException) as excinfo:
        get_repository_files("https://github.com/test_user/nonexistent_repo")

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Failed to fetch repository files"


# Тест на помилку декодування вмісту файлу
@patch("src.services.github_fetcher.g.get_repo")
def test_get_repository_files_decode_error(mock_get_repo):
    mock_file = type('FileContent', (object,), {'type': 'file', 'name': 'test_file.py', 'decoded_content': None})
    mock_get_repo.return_value.get_contents.return_value = [mock_file]

    with pytest.raises(HTTPException) as excinfo:
        get_repository_files("https://github.com/test_user/repo_with_invalid_file")

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Failed to fetch repository files"
