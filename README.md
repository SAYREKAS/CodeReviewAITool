# Instructions for Running the Dockerized Application

This document provides instructions on how to build and run the application using Docker Compose.

## Prerequisites

 - Ensure that Docker and Docker Compose are installed on your system.
 - You will need your GITHUB_ACCESS_TOKEN and OPENAI_API_KEY.

## Instructions

### 1. Clone the Repository

Open a terminal (or command prompt), and execute the following command to clone the repository to your local machine:

```bash
git clone https://github.com/SAYREKAS/CodeReviewAITool.git
````

Navigate to the directory of the cloned repository:

```bash
cd CodeReviewAITool
````

### 2. Docker Compose Configuration
In this directory, create a new file named docker-compose.yml. You can use a text editor such as nano, vim, or any graphical text editor:

```bash
touch docker-compose.yml
````

Open the docker-compose.yml file and insert the following configuration:

```bash
version: '3.9'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - GITHUB_ACCESS_TOKEN=<your_github_access_token>
      - OPENAI_API_KEY=<your_openai_api_key>

  redis:
    image: "redis:latest"
    ports:
      - "6379:6379"
````

Note: Be sure to replace <your_github_access_token> and <your_openai_api_key> with your actual values.

### 3. Build and Run the Docker Containers

To start the containers, use the command:

```bash
docker compose up --build -d
````

This command:

	•	--build: forces the images to be built, even if they already exist.
	•	-d: runs the containers in detached mode, allowing you to continue using the terminal.

### 4. Check Logs (Optional)

To view the logs of the running application container, use the following command:

```bash
docker compose logs -f
````

### 5. Access the Application

You can access your application through your web browser at:

http://localhost:8001

### 6. Stop Docker Containers (Optional)

You can stop all Docker containers for the current project by entering the following command:

```bash
docker compose down
````

## Additional Notes

	•	If port 8001 is already in use, you can choose another port by modifying the ports section in the docker-compose.yml file. For example, change "8001:8000" to "8888:8000" to use port 8888 on your computer.
	•	Make sure that Redis is running correctly. If you encounter issues with the application, check the Redis logs for more information.