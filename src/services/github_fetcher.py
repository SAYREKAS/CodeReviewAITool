import os
import httpx
import asyncio

from loguru import logger
from dotenv import load_dotenv
from fastapi import HTTPException

from src.services.data_structures import RepoFilesResponse, Content

load_dotenv()

GITHUB_API_URL = "https://api.github.com"

logger.remove()
logger.add(sink=lambda msg: print(msg, end=""), colorize=True)

GITHUB_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


async def get_repository_files(repo_url: str) -> RepoFilesResponse:
    """
    Fetches files from a specified GitHub repository using the GitHub API.

    Args:
        repo_url (str): The URL of the GitHub repository.

    Returns:
        RepoFilesResponse: A response object containing the list of files and their count.

    Raises:
        HTTPException: If the repository URL is invalid or if an error occurs during file retrieval.
    """
    try:
        logger.info(f"Fetching files from repository: {repo_url}")

        # Extract owner and repository name from URL
        parts = repo_url.split("/")
        if len(parts) < 5 or parts[2] != "github.com":
            raise HTTPException(status_code=404, detail="Invalid GitHub repository URL")

        owner = parts[3]
        repo_name = parts[4]
        logger.debug(f"Owner: {owner}, Repository: {repo_name}")

        # Fetch repository contents from GitHub API
        api_url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/contents"
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=HEADERS)
            if response.status_code != 200:
                logger.error(f"Failed to fetch repository contents: {response.status_code}")
                raise HTTPException(status_code=404, detail="Failed to fetch repository files")

            root_contents = response.json()

        file_contents: list[Content] = []

        async def get_files_in_directory(contents, client, current_path="", depth=0, max_depth=100):
            """
            Recursive function to traverse repository directories with depth control.

            Args:
                contents: The contents of the current directory.
                client: Shared HTTPX client for making requests.
                current_path (str): The path of the current directory being traversed.
                depth (int): The current depth of recursion.
                max_depth (int): The maximum allowed recursion depth.
            """
            if depth > max_depth:
                logger.error(f"Maximum recursion depth {max_depth} reached at {current_path}")
                return

            tasks = []
            for content in contents:
                if content["type"] == "dir":
                    logger.debug(f"Traversing directory: {content['path']}")
                    tasks.append(fetch_directory_content(content["url"], client, current_path, depth, max_depth))
                else:
                    tasks.append(fetch_file_content(content, client, current_path))

            await asyncio.gather(*tasks)

        async def fetch_directory_content(url, client, current_path, depth, max_depth):
            """Fetch contents of a directory and recursively call get_files_in_directory."""
            dir_response = await client.get(url, headers=HEADERS)
            if dir_response.status_code != 200:
                logger.error(f"Failed to fetch directory contents: {dir_response.status_code}")
                return
            dir_contents = dir_response.json()
            await get_files_in_directory(dir_contents, client, current_path, depth + 1, max_depth)

        async def fetch_file_content(content, client, current_path):
            """Fetch the content of a file and append it to file_contents."""
            try:
                full_path = current_path + content["name"]
                logger.debug(f"Fetching file: {full_path}")
                file_response = await client.get(content["download_url"], headers=HEADERS)
                if file_response.status_code != 200:
                    logger.error(f"Failed to fetch file: {file_response.status_code}")
                    return
                file_contents.append(Content(filename=full_path, file_content=file_response.text))
            except Exception as ex:
                logger.error(f"Error fetching file {content['path']}: {ex}")

        # Recursively fetch files starting from the root directory
        async with httpx.AsyncClient() as client:
            await get_files_in_directory(root_contents, client)

        logger.info(f"Retrieved {len(file_contents)} files from repository {repo_name}")
        return RepoFilesResponse(files=file_contents, count=len(file_contents))

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as ex:
        logger.error(f"Error: {ex}")
        raise HTTPException(status_code=404, detail="Failed to fetch repository files")
