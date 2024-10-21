
# Instructions for Running the Dockerized Application

This document provides instructions on how to build and run the application using Docker.

## Prerequisites

- Docker must be installed on your system.
- You need to have your `GITHUB_ACCESS_TOKEN` and `OPENAI_API_KEY` available.

## Instructions

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/SAYREKAS/CodeReviewAITool.git
cd CodeReviewAITool
```

### 2. Build the Docker Image

Navigate to the project directory where your Dockerfile is located and build the Docker image:

```bash
docker build . -t code_review_ai_tool
```

### 3. Run the Docker Container

Start the Docker container with the required environment variables:

```bash
docker run -e GITHUB_ACCESS_TOKEN='your_token' -e OPENAI_API_KEY='your_api_key' -p 8000:8000 --name code_review_ai_tool_container -d code_review_ai_tool
```

### 4. Check Logs (Optional)

To view the logs of the running container, use the following command:

```bash
docker logs -f code_review_ai_tool_container
```

### 5. Access the Application

You can access the application in your web browser at:

[http://localhost:8000](http://localhost:8000)

## Notes

- Make sure to replace `your_token` and `your_api_key` with your actual API keys.
- If port 8000 is already in use, you can choose another port by modifying the `-p` option in the `docker run` command. For example:
  ```bash
  docker run -p 8888:8000 code_review_ai_tool_container
  ```
  Here, port `8888` on your computer will be forwarded to port `8000` inside the container.
