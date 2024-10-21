import os

from github import Auth
from github import Github
from loguru import logger
from dotenv import load_dotenv

from src.services.data_structures import Content

load_dotenv()

auth = Auth.Token(os.getenv('GITHUB_ACCESS_TOKEN'))
g = Github(auth=auth)


def get_repository_files(repo_url: str) -> list[Content] | None:
    try:
        logger.info(f"Fetching files from repository: {repo_url}")

        # Extract owner and repository name from URL
        parts = repo_url.split("/")
        if len(parts) < 5 or parts[2] != "github.com":
            raise ValueError("Invalid GitHub repository URL")

        owner = parts[3]
        repo_name = parts[4]

        logger.debug(f"Owner: {owner}, Repository: {repo_name}")

        repo = g.get_repo(f"{owner}/{repo_name}")

        file_contents: list[Content] = []

        def get_files_in_directory(contents):
            """Recursive function to traverse repository directories"""
            for content in contents:
                if content.type == "dir":
                    logger.debug(f"Traversing directory: {content.path}")
                    get_files_in_directory(repo.get_contents(content.path))
                else:
                    try:
                        logger.debug(f"Fetching file: {content.path}")
                        decoded_content = content.decoded_content.decode('utf-8')
                        file_contents.append(Content(filename=content.path, file_content=decoded_content))
                    except Exception as e:
                        logger.error(f"Error decoding file {content.path}: {e}")

        # Get contents of the root directory
        root_contents = repo.get_contents("")
        get_files_in_directory(root_contents)

        logger.info(f"Retrieved {len(file_contents)} files from repository {repo_name}")
        return file_contents

    except Exception as e:
        logger.error(f"Error: {e}")
        return None
