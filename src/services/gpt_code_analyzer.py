import os
import json

from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv
from fastapi import HTTPException

from src.services.data_structures import CandidateLevel, AnalysisReport, RepoFilesResponse, Content

load_dotenv()


class GPTCandidateAnalyzer:
    __CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def __init__(self, file_contents: RepoFilesResponse, candidate_level: CandidateLevel, assignment_description: str):
        if not file_contents.files:
            raise HTTPException(status_code=400, detail="The file content is missing. Please check the repository URL.")

        self.__files_contents = file_contents.files
        self.__candidate_level = candidate_level
        self.__assignment_description = assignment_description

        self.file_analysis_parts: list[str] = []
        self.project_files: list[str] = []

        self.analysis_report: AnalysisReport | None = None

        self.__start()

    def __gpt_api_response(self, prompt: str, model: str = "gpt-4-turbo") -> str:
        try:
            response = self.__CLIENT.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a code reviewer."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error during GPT analysis: {e}")
            raise HTTPException(status_code=500, detail="An internal error occurred while processing the analysis.")

    def __analyze_file_part(self, content: Content, part: str, part_index: int, total_parts: int) -> str:
        if total_parts == 1:
            prompt = f"""
            {self.__assignment_description}\n\n
            File '{content.filename}'.
            Candidate level: {self.__candidate_level}.
            Code: {part}
            """
        else:
            prompt = f"""
            {self.__assignment_description}\n\n
            Part {part_index}/{total_parts} of the file '{content.filename}'.
            Candidate level: {self.__candidate_level}.
            Code: {part}
            """

        return self.__gpt_api_response(prompt)

    @staticmethod
    def __parse_json_response(response: str) -> dict:
        try:
            json_data = json.loads(response)
            return json_data

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise HTTPException(status_code=422, detail="The analysis could not be completed. Please try again.")

    def __analyze_files(self) -> None:
        if not self.__files_contents:
            raise HTTPException(status_code=404, detail="No files available for analysis. Please check the repository.")

        for content in self.__files_contents:
            self.project_files.append(content.filename)
            logger.info(f"Analyzing file: {content.filename}")

            split_file_content = [
                content.file_content[i:i + 7000] for i in range(0, len(content.file_content), 7000)
            ]

            total_parts = len(split_file_content)

            for part_index, part in enumerate(split_file_content, start=1):
                logger.debug(f"Sending part {part_index} of file {content.filename} for analysis")

                try:
                    analysis_part = self.__analyze_file_part(content, part, part_index, total_parts)
                    self.file_analysis_parts.append(
                        f"File {content.filename}, part {part_index}/{total_parts}:\n{analysis_part}"
                        if total_parts > 1 else
                        f"File {content.filename}:\n{analysis_part}"
                    )

                except Exception as e:
                    logger.error(f"Error analyzing part {part_index} of file {content.filename}: {e}")
                    raise HTTPException(status_code=500,
                                        detail="An error occurred while analyzing the file. Please try again.")

        logger.info("File analysis completed.")

    def __generate_final_report(self) -> None:
        full_report = "\n\n".join(self.file_analysis_parts)
        prompt = f"""
        Please analyze the following code and provide a structured report in JSON format with the following fields:
        - 'flaws': A list of specific issues found in the code.
        - 'rating': A rating of the candidate's performance (e.g., 1-5 or a detailed textual description).
        - 'conclusion': A final assessment of the code quality and areas for improvement.

        The analysis is based on the candidate's level '{self.__candidate_level}' and the following code analysis:
        {full_report}
        """

        try:
            overall_analysis = self.__gpt_api_response(prompt)
            structured_data = self.__parse_json_response(overall_analysis)

            self.analysis_report = AnalysisReport(
                project_files=self.project_files,
                full_report=full_report,
                conclusion_and_assessment=structured_data,
            )
            logger.info("Final structured conclusion and candidate rating in JSON format received.")

        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while generating the final report.")

    def __start(self) -> None:
        self.__analyze_files()
        self.__generate_final_report()
