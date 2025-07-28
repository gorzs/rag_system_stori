# rag_system_stori
This project is a Retrieval-Augmented Generation (RAG) system designed to answer questions about the Mexican Revolution.  It combines a local LLM (`google/flan-t5-base`) with context retrieval from vectorized documents. 


# Mexican Revolution RAG chatbot
The system includes:

- **React frontend**
- **FastAPI backend**
- **Prometheus + Grafana** for monitoring
- **Human escalation via email**
- **Docker for containerization**
- **Cloud-ready infrastructure with AWS CDK**

---

## Features

- Real-time chat with conversation history (stored in SQLite)
- Context-aware RAG answers
- Monitoring metrics: 
    - Total questions and users
    - Escalation rate and escalation volume
    - Retrieval and generation latency
    - Prompt token usage
    - Generation failures
- Grafana dashboard for live insights
- Auto-escalation via email to human agents
- Ready to deploy in the cloud

---

## Project structure

```
rag-chatbot/
 └── frontend/  # React app
 └── backend/  # FastAPI app
 └── grafana/  # Dashboard configs
 └── cdk/  # AWS CDK code
 └── docker-compose.yml
 └──README.md # this file

```

---

## Local deployment with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/gorzs/rag_system_stori.git
   cd rag_system_stori
   ```

2. Copy and edit the environment file:
   ```bash
   cp .env.example .env
   ```

3. Launch the full system:
   ```bash
   docker-compose up --build
   ```

4. Access services:
   - Chatbot: http://localhost:3000
   - Backend: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001 (user: admin, pass: admin)
		-To load the custom dashboard:
			- Go to the left sidebar menu > "Dashboards" > "Import"
			- Click on "Upload JSON file".
			- Select the file ./grafana/dashboards/fastapi_bot_dashboard.json.
			- Link the data source (Prometheus) and click "Import".

---

## Grafana dashboard and monitoring

The Grafana dashboard includes:

- Total requests: Total number of API requests handled by the system
- Errors (4xx + 5xx): Count of client and server errors for identifying failures
- Latency by endpoint: Request latency averaged over time, segmented by API route
- Requests by handler and method: Table showing the volume of requests broken down by route and HTTP method 
- GC collections (Gen 2): Number of Python garbage collection events for generation 2

Import the dashboard from `grafana/dashboard.json`.

The custom /metrics/escalations endpoint enriches the monitoring feature by exposing:

| Escalation metric         | Description                                                                                 |
|---------------------------| ------------------------------------------------------------------------------------------- |
| `total_escalated_users`   | Number of unique users who were escalated at least once                                     |
| `total_escalation_cases`  | Total number of escalation events triggered                |
| `total_users`             | Total number of users who interacted with the system                                        |
| `total_questions`         | Total number of questions asked by all users                                                |
| `escalation_rate_percent` | Percentage of questions that resulted in an escalation (`total_escalation_cases / total_questions * 100`) |


---

## Cloud deployment (AWS CDK)

1. Install AWS CLI and CDK:
   ```bash
   npm install -g aws-cdk
   aws configure
   ```

2. Navigate to CDK folder:
   ```bash
   cd cdk/
   ```

3. Install dependencies and deploy:
   ```bash
   python -m venv .venv
	source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

	pip install -r requirements.txt
   ```
4. Bootstrap the AWS environment:
   ```bash
   cdk bootstrap
   ```
5. Deploy:
   ```bash
   cdk deploy
   ```

This deploys:

- A VPC and ECS Fargate cluster
- Frontend and backend containers behind an Application Load Balancer
- S3 bucket for persistent storage
- CloudWatch Logs for observability

---

## Email escalation

When escalation is needed, the backend sends an email to registered agents. Configure recipients in `backend/tools.py`.

---

## Security

- AWS credentials are set using `aws configure` (never stored in code)
- Use environment variables for secrets

---

## Tech stack used

- FastAPI + Uvicorn
- React
- SentenceTransformers
- Hugging Face Transformers
- Prometheus + Grafana
- Docker & Docker Compose
- AWS CDK (Python)

---

## Improvements if I had more time

- Migrate context store to Pinecone/OpenSearch
- Migrate from SQLite to a scalable database (e.g., PostgreSQL or DynamoDB) to support concurrent users and enable horizontal scaling in production environments
- Add user authentication
- Add real-time notification for escalations
- Generate balance escalations across multiple agents
- Replace Grafana with Amazon CloudWatch Dashboards, allowing all chatbot metrics (including total questions, escalations, latency, and error rates) to be collected, visualized, and alerted directly within the AWS ecosystem
---

## Developer

Built by Gabriela Ortíz
Contact: [gabortzsanz@gmail.com](mailto:gabortzsanz@gmail.com)
