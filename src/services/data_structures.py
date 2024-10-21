from enum import Enum

from pydantic import BaseModel


class CandidateLevel(Enum):
    junior = "junior"
    middle = "middle"
    senior = "senior"


class Content(BaseModel):
    filename: str
    file_content: str
    file_parts: list[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.file_parts = self.split_file_content()

    def split_file_content(self, max_size: int = 7000) -> list[str]:
        return [self.file_content[i:i + max_size] for i in range(0, len(self.file_content), max_size)]
