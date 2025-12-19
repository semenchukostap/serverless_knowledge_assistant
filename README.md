# Serverless Knowledge Assistant

A serverless RAG (Retrieval-Augmented Generation) application built on AWS that allows users to query technical documentation using natural language. This PoC demonstrates a serverless-first architecture using Amazon Bedrock Knowledge Base, Lambda, and API Gateway.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment](#deployment)
- [User Interface](#user-interface)
- [Testing](#testing)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Cleanup](#cleanup)
- [Cost Estimation](#cost-estimation)
- [Project Structure](#project-structure)

---

## Overview

This project implements a serverless knowledge assistant that:
- Ingests PDF documents into Amazon Bedrock Knowledge Base
- Provides a REST API endpoint for natural language queries
- Uses RAG (Retrieval-Augmented Generation) to answer questions based on ingested documents
- Follows serverless-first architecture principles
- Implements least-privilege IAM policies

### Key Features

- **Serverless Architecture**: Lambda, API Gateway, Bedrock, S3 Vectors
- **Infrastructure as Code**: Terraform for all AWS resources
- **RAG Pipeline**: Bedrock Knowledge Base with vector search
- **Python 3.11**: Lambda runtime with Pydantic validation
- **Least-Privilege Security**: Scoped IAM permissions
- **S3 Static Website**: Web UI with auto-configured API endpoint

---

## Architecture

### Components

1. **S3 Static Website**: Web UI hosted on S3 static website hosting
2. **API Gateway HTTP API**: RESTful endpoint (`POST /query`)
3. **Lambda Function**: Python handler for query processing
4. **Bedrock Knowledge Base**: RAG service with vector search
5. **S3 Vectors**: Native AWS vector storage for embeddings
6. **S3 Buckets**: Document storage (source), vector storage, and UI hosting
7. **IAM Roles**: Least-privilege permissions for all services

### Data Flow

```
User Query
    ↓
API Gateway HTTP API (POST /query)
    ↓
Lambda Function (handler.py)
    ↓
Bedrock Knowledge Base (Retrieve API)
    ↓
S3 Vectors (Vector Search)
    ↓
Bedrock Foundation Model (Nova Micro/Pro)
    ↓
Generated Answer
    ↓
API Gateway Response
```

### Technology Stack

- **Compute**: AWS Lambda (Python 3.11)
- **API**: API Gateway HTTP API v2
- **AI/ML**: Amazon Bedrock (Nova Micro, Titan Embeddings)
- **Vector DB**: Amazon S3 Vectors (native AWS solution)
- **Storage**: S3 (documents and vectors)
- **IaC**: Terraform
- **Validation**: Pydantic

---

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **Docker** installed and running (required for building Lambda packages)
4. **uv** installed (recommended Python package manager)
   - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
5. **Python 3.11+** (for local testing and development)
6. **AWS Account** with Bedrock access enabled
7. **Make** (optional, for using Makefile commands)

### Docker Requirement

**Docker is required** to build Lambda-compatible Python packages. The build process uses Docker to install dependencies in a Linux x86_64 environment

**Verify Docker is running:**
```bash
docker --version
docker ps
```

### Enable Bedrock Access

**IMPORTANT:** Bedrock foundation models must be activated before use. This is a one-time setup per AWS account.

#### Required Models

- **Titan Embeddings G1 - Text** (`amazon.titan-embed-text-v1`) - For generating embeddings
- **Nova Micro** (`amazon.nova-micro-v1:0`) - For text generation (default, can be changed to Nova Pro)

#### Verify Model Access

```bash
aws bedrock list-foundation-models --by-output-modality EMBEDDING --query "modelSummaries[?modelId=='amazon.titan-embed-text-v1']"

aws bedrock list-foundation-models --by-provider amazon --query "modelSummaries[?modelId=='amazon.nova-micro-v1:0']"
```

**Note:** Ensure Nova Micro (or Nova Pro if using that model) access is enabled in your AWS account. Some models may require provisioned throughput or specific region availability.

---

## Installation

1. **Clone the repository** (if applicable)

2. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create and activate virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

4. **Install dependencies**:
   ```bash
   # Install all dependencies including dev tools (pytest, ruff, etc.)
   uv sync --extra dev
   
   # Or install only production dependencies
   uv sync
   ```

---

## Deployment

### Quick Start

```bash
# Initialize Terraform
make init

# Validate configuration
make validate

# Review deployment plan
make plan

# Deploy infrastructure
make deploy
```

The `make deploy` command will:
1. **Build Lambda package** (automatically installs dependencies using Docker)
2. **Apply Terraform configuration** (deploys infrastructure)
3. **Start Bedrock Knowledge Base ingestion job**
4. **Display UI Website URL** (automatically shown after deployment)

**Note:** The build process requires Docker to be running. If Docker is not available, the build will fail with a clear error message.

### Deployment Outputs

After successful deployment, the UI Website URL is automatically displayed:

```
Deployment complete!

UI Website URL:
http://knowledge-assistant-ui-XXXXXXXXX.s3-website-<region>.amazonaws.com
```

**Note:** The `<region>` in the URL matches your configured AWS region (default: `us-east-1`).

To view all outputs:

```bash
make output
```

**Key Outputs:**
- `ui_website_url`: Public URL for the S3-hosted web interface
- `api_gateway_query_endpoint`: Full URL for POST `/query` endpoint (automatically configured in UI)
- `bedrock_knowledge_base_id`: Knowledge Base ID for verification
- `lambda_function_name`: Lambda function name for CloudWatch logs

---

## User Interface

The web interface is hosted on **AWS S3 static website hosting** and is automatically deployed with your infrastructure. The API Gateway endpoint is automatically configured in the UI during deployment - no manual configuration needed!

### Accessing the UI

After running `make deploy`, the UI Website URL is automatically displayed. Simply open the URL in your browser to start using the interface.

### How to Use

1. **Open the UI Website URL** (shown after `make deploy`)

2. **Ask Questions:**
   - Type your question about the AWS Serverless Applications Lens whitepaper in the text area
   - Click "Ask Question" to submit
   - View the answer generated from the AWS Serverless Applications Lens document

### Features

- **Auto-configured API endpoint** - API Gateway URL automatically injected during deployment
- **Copy to clipboard** - Easy answer copying
- **Query history** - Access your last 5 queries (stored in browser localStorage)
- **Loading indicators** - Visual feedback during processing
- **Mobile-friendly** - Responsive design for all devices

---

## Testing

### Unit Tests

Run unit tests with pytest:

```bash
# Run all tests with verbose output
pytest -v
# or
make test

# Run only Lambda function tests (mocked, no AWS credentials needed)
make test-lambda

# Run only infrastructure tests (requires AWS credentials and deployed resources)
make test-infra
```

**Prerequisites for Infrastructure Tests:**
- AWS credentials configured (`aws configure` or environment variables)
- Resources deployed via `make deploy`
- Terraform outputs available (`make output`)

### Test Coverage

The project is configured to require 80% code coverage:

```bash
# Run tests with coverage report
pytest --cov=lambda --cov-report=html

# View HTML coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

### Code Quality

The project uses `ruff` for linting and formatting:

```bash
# Run linter (check for issues)
make lint

# Run linter and auto-fix issues
make lint-fix
```

**Note:** Install dev dependencies first: `uv sync --extra dev`

### Verify Bedrock Knowledge Base Ingestion

Check if the PDF has been ingested:

```bash
make check
```

**Expected Status:** `COMPLETE` or `IN_PROGRESS`

**Note:** Ingestion can take 5-15 minutes depending on PDF size.

### Test API Endpoint

Test the Lambda function via API Gateway:

```bash
API_URL=$(cd terraform && terraform output -raw api_gateway_query_endpoint)

curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key principles of serverless architecture?"
  }'
```

**Expected Response:**
```json
{
  "answer": "The key principles of serverless architecture, as outlined in the context provided from the AWS Well-Architected Framework, are..."
}
```

---

## Monitoring & Troubleshooting

### CloudWatch Logs

View Lambda function logs:

```bash
make logs
```

**Note:** CloudWatch Log groups are automatically created when the Lambda function is first invoked. If you see "log group does not exist", make a test API call to the endpoint first.

### Verify Infrastructure

```bash
cd terraform

# List all resources
terraform state list

# Show specific resource
terraform state show aws_lambda_function.knowledge_assistant

# Verify Lambda function exists
aws lambda get-function \
  --function-name $(terraform output -raw lambda_function_name)

# Verify Knowledge Base exists
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id $(terraform output -raw bedrock_knowledge_base_id)
```

---

## Cleanup

Destroy all resources:

```bash
make destroy
```

**Warning:** This will delete all resources.

---

## Cost Estimation

### Expected Monthly Costs (PoC Usage - 1M requests/month):

- **Lambda Requests**: ~$0.20
  - `1M requests (after free tier) x $0.20 per million = $0.20`
- **Lambda Compute**: ~$2.13-5.33
  - `1M requests x 1-2.5s duration x 128MB = 128K-320K GB-seconds`
  - `128K-320K GB-seconds x $0.0000166667/GB-second = $2.13-5.33`
- **API Gateway HTTP API**: ~$1.00
  - `1M requests x $1.00 per million = $1.00`
- **Bedrock Knowledge Base**: 
  - **Retrieve API**: ~$0.10-0.30
    - `1M requests (varies by region and data size)`
  - **Nova Micro**: ~$45.50-210.00
    - Input: `1M requests x 500-2000 tokens x $0.035/M = $17.50-70.00`
    - Output: `1M requests x 200-1000 tokens x $0.14/M = $28.00-140.00`
    - Total: `$17.50-70.00 + $28.00-140.00 = $45.50-210.00`
- **Titan Embeddings**: ~$0.02-0.10 (for document ingestion, one-time or minimal recurring)
- **S3 Vectors**: ~$0.01-0.10 (storage + requests, minimal cost)
- **S3 Documents**: ~$0.01 (storage + requests, minimal cost)
- **S3 UI Hosting**: ~$0.01-0.05 (storage + GET requests + data transfer, minimal cost)

**Total Estimated:** ~$49-217/month for PoC usage (1M requests)

**Note:** 
- Lambda function uses 128MB memory (default) with 12 second timeout
- **Nova Micro Pricing**: 
  - Input tokens: `$0.035 per million tokens`
  - Output tokens: `$0.14 per million tokens`
- Bedrock costs vary significantly based on query complexity, context length, and response length
- Token usage depends on KB retrieval results (typically 500-2000 input tokens including context)
- **S3 Vectors provides cost-effective vector storage** (approximately `<$1/month` for vector storage)
- Actual costs depend on usage volume, region, and data transfer. Monitor via AWS Cost Explorer.

---

## Project Structure

```
serverless_knowledge_assistant/
├── terraform/                      # Terraform infrastructure code
│   ├── api_gateway.tf              # API Gateway HTTP API configuration
│   ├── bedrock.tf                  # Bedrock Knowledge Base setup
│   ├── iam.tf                      # IAM roles and policies
│   ├── lambda.tf                   # Lambda function definition
│   ├── s3.tf                       # S3 bucket configuration
│   ├── ui.tf                       # S3 static website hosting for UI
│   ├── providers.tf                # Terraform provider configuration
│   ├── variables.tf                # Terraform variables
│   └── outputs.tf                  # Terraform outputs
├── lambda/                         # Lambda function code
│   ├── handler.py                  # Lambda handler (API Gateway integration)
│   ├── bedrock_client.py           # Bedrock Knowledge Base client
│   └── schemas.py                  # Pydantic request/response schemas
├── tests/                          # Unit tests (not included in Lambda deployment)
│   ├── lambda/                     # Lambda function tests
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest fixtures for Lambda tests
│   │   ├── test_handler.py         # Handler tests
│   │   ├── test_bedrock_client.py  # Bedrock client tests
│   │   └── test_schemas.py         # Schema validation tests
│   └── terraform/                  # Terraform infrastructure tests
│       ├── __init__.py
│       ├── conftest.py             # Pytest fixtures for infrastructure tests
│       ├── test_lambda.py          # Lambda infrastructure tests
│       ├── test_api_gateway.py     # API Gateway infrastructure tests
│       ├── test_s3.py              # S3 bucket infrastructure tests
│       └── test_bedrock.py         # Bedrock Knowledge Base infrastructure tests
├── ui/                             # Static HTML UI for S3 website hosting
│   ├── index.html                  # Main UI interface (API Gateway URL auto-injected)
│   └── styles.css                  # UI stylesheet
├── build_lambda.sh                 # Build script (requires Docker and uv)
├── knowledge-base/                 # Source documents for Bedrock Knowledge Base
│   └── wellarchitected-serverless-applications-lens.pdf
├── pyproject.toml                  # Python project configuration and dependencies
├── uv.lock                         # Locked dependencies (uv)
├── Makefile                        # Deployment automation commands
├── GenAI PoC Serverless Knowledge Assistant.pdf  # Technical handover presentation 
├── .gitignore                      # Git ignore patterns
└── README.md                       # This file
```
