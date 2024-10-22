import os

from loguru import logger
from dotenv import load_dotenv
from github import Auth, Github
from fastapi import HTTPException

from src.services.data_structures import RepoFilesResponse, Content

load_dotenv()

logger.remove()
logger.add(sink=lambda msg: print(msg, end=""), colorize=True)

auth = Auth.Token(os.getenv('GITHUB_ACCESS_TOKEN'))
g = Github(auth=auth)


def get_repository_files(repo_url: str) -> RepoFilesResponse:
    """
    Fetches files from a specified GitHub repository.

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

        repo = g.get_repo(f"{owner}/{repo_name}")

        file_contents: list[Content] = []

        def get_files_in_directory(contents, current_path="", depth=0, max_depth=100):
            """
            Recursive function to traverse repository directories with depth control.

            Args:
                contents: The contents of the current directory.
                current_path (str): The path of the current directory being traversed.
                depth (int): The current depth of recursion.
                max_depth (int): The maximum allowed recursion depth.
            """
            if depth > max_depth:
                logger.error(f"Maximum recursion depth {max_depth} reached at {current_path}")
                return

            for content in contents:
                if content.type == "dir":
                    logger.debug(f"Traversing directory: {content.path}")
                    get_files_in_directory(
                        repo.get_contents(content.path), current_path + content.name + "/", depth + 1, max_depth
                    )
                else:
                    try:
                        full_path = current_path + content.name
                        logger.debug(f"Fetching file: {full_path}")
                        decoded_content = content.decoded_content.decode('utf-8')
                        file_contents.append(Content(filename=full_path, file_content=decoded_content))

                    except Exception as ex:
                        logger.error(f"Error decoding file {content.path}: {ex}")

        # Get contents of the root directory
        root_contents = repo.get_contents("")
        get_files_in_directory(root_contents)

        logger.info(f"Retrieved {len(file_contents)} files from repository {repo_name}")
        return RepoFilesResponse(files=file_contents, count=len(file_contents))

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as ex:
        logger.error(f"Error: {ex}")
        raise HTTPException(status_code=404, detail="Failed to fetch repository files")
