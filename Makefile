.PHONY: help init fmt validate plan apply destroy start-ingestion deploy clean output check logs package test test-infra test-lambda lint lint-fix

# Default target
help:
	@echo "Available targets:"
	@echo "  make init           - Initialize Terraform"
	@echo "  make fmt            - Format Terraform files"
	@echo "  make validate       - Validate Terraform configuration"
	@echo "  make plan           - Show Terraform execution plan"
	@echo "  make package        - Build Lambda deployment package (build/lambda_package.zip)"
	@echo "  make apply          - Apply Terraform configuration"
	@echo "  make destroy        - Destroy all Terraform resources"
	@echo "  make start-ingestion - Start Bedrock ingestion job"
	@echo "  make deploy         - Apply Terraform and start ingestion job"
	@echo "  make output         - Show all Terraform outputs"
	@echo "  make check          - Check Bedrock ingestion job status"
	@echo "  make logs           - View last Lambda function logs"
	@echo "  make test           - Run all tests (Lambda + infrastructure)"
	@echo "  make test-lambda    - Run Lambda function tests (mocked, no AWS needed)"
	@echo "  make test-infra     - Run infrastructure tests (requires AWS credentials)"
	@echo "  make lint           - Run linter (ruff) on Python code"
	@echo "  make lint-fix       - Run linter and auto-fix issues"
	@echo "  make clean          - Clean up Terraform state files and build artifacts"

# Terraform directory
TF_DIR := terraform

# Initialize Terraform
init:
	cd $(TF_DIR) && terraform init

# Format Terraform files
fmt:
	@echo "Formatting Terraform files..."
	cd $(TF_DIR) && terraform fmt -recursive

# Validate Terraform configuration
validate:
	@echo "Validating Terraform configuration..."
	cd $(TF_DIR) && terraform validate

# Show Terraform plan
plan:
	@echo "Generating Terraform execution plan..."
	cd $(TF_DIR) && terraform plan

# Build Lambda deployment package
# Creates build/lambda_package/ with source code and dependencies, then zips it
package:
	@./build_lambda.sh

# Apply Terraform configuration
apply: package
	@echo "Applying Terraform configuration..."
	cd $(TF_DIR) && terraform apply -auto-approve

# Destroy all resources
destroy:
	cd $(TF_DIR) && terraform destroy -auto-approve

# Start Bedrock ingestion job
start-ingestion:
	@echo "Starting Bedrock ingestion job..."
	@cd $(TF_DIR) && \
		KB_ID=$$(terraform output -raw bedrock_knowledge_base_id) && \
		DS_ID=$$(terraform output -raw bedrock_data_source_id) && \
		REGION=$$(terraform output -raw aws_region) && \
		aws bedrock-agent start-ingestion-job \
			--knowledge-base-id $$KB_ID \
			--data-source-id $$DS_ID \
			--region $$REGION \
			--output json || \
		echo "Note: Ingestion job may already be running or completed. Use 'make check' to verify status."

# Deploy: Apply Terraform and start ingestion
deploy: apply start-ingestion
	@echo "Deployment complete!"
	@echo ""
	@echo "UI Website URL:"
	@cd $(TF_DIR) && terraform output -raw ui_website_url && echo

# Show Terraform outputs
output:
	@echo "Terraform outputs:"
	@cd $(TF_DIR) && terraform output

# Check Bedrock ingestion job status
check:
	@echo "Checking Bedrock ingestion job status..."
	@cd $(TF_DIR) && \
		KB_ID=$$(terraform output -raw bedrock_knowledge_base_id 2>/dev/null) && \
		DS_ID=$$(terraform output -raw bedrock_data_source_id 2>/dev/null) && \
		REGION=$$(terraform output -raw aws_region 2>/dev/null) && \
		if [ -z "$$KB_ID" ] || [ -z "$$DS_ID" ] || [ -z "$$REGION" ]; then \
			echo "Error: Terraform outputs not available. Run 'make deploy' first."; \
			exit 1; \
		fi && \
		aws bedrock-agent list-ingestion-jobs \
			--knowledge-base-id $$KB_ID \
			--data-source-id $$DS_ID \
			--region $$REGION \
			--max-results 5 \
			--output table || \
		echo "Error: Failed to check ingestion status. Ensure AWS CLI is configured."

# View Lambda function logs
logs:
	@echo "Fetching last Lambda function logs..."
	@cd $(TF_DIR) && \
		FUNCTION_NAME=$$(terraform output -raw lambda_function_name 2>/dev/null) && \
		if [ -z "$$FUNCTION_NAME" ]; then \
			echo "Error: Terraform outputs not available. Run 'make deploy' first."; \
			exit 1; \
		fi && \
		LOG_GROUP="/aws/lambda/$$FUNCTION_NAME" && \
		echo "Log group: $$LOG_GROUP" && \
		echo "Fetching logs from last 5 minutes..." && \
		echo "---" && \
		aws logs filter-log-events \
			--log-group-name $$LOG_GROUP \
			--start-time $$(($$(date +%s) - 300))000 \
			--max-items 50 \
			--query 'events[*].message' \
			--output text 2>/dev/null || \
		echo "Error: Failed to retrieve logs. Ensure AWS CLI is configured and log group exists."

# Run all tests
test:
	@echo "Running all tests..."
	pytest -v

# Run Lambda function tests (mocked, no AWS credentials needed)
test-lambda:
	@echo "Running Lambda function tests..."
	pytest tests/lambda/ -v

# Run infrastructure tests (requires AWS credentials and deployed resources)
test-infra:
	@echo "Running infrastructure tests..."
	@echo "Prerequisites: AWS credentials configured and resources deployed via 'make deploy'"
	pytest tests/terraform/ -v

# Run linter on Python code
lint:
	@echo "Running linter (ruff)..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check lambda/ tests/; \
		ruff format --check lambda/ tests/; \
	else \
		echo "Error: ruff not found. Install dev dependencies with: uv sync"; \
		exit 1; \
	fi

# Run linter and auto-fix issues
lint-fix:
	@echo "Running linter and auto-fixing issues..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check --fix lambda/ tests/; \
		ruff format lambda/ tests/; \
	else \
		echo "Error: ruff not found. Install dev dependencies with: uv sync"; \
		exit 1; \
	fi

# Clean up Terraform state files, build artifacts, and Python packages
clean:
	@echo "Cleaning up Terraform state files..."
	cd $(TF_DIR) && rm -f terraform.tfstate.backup terraform.tfstate.*.backup tfplan
	@echo "Cleaning up build artifacts..."
	rm -rf build/
	@echo "Cleaning up Python packages from lambda directory..."
	@cd lambda && find . -maxdepth 1 -type d \( -name "boto3" -o -name "botocore" -o -name "pydantic*" -o -name "typing_extensions" -o -name "jmespath" -o -name "s3transfer" -o -name "urllib3" -o -name "dateutil" -o -name "annotated_types" -o -name "typing_inspection" -o -name "*.dist-info" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true
	@cd lambda && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@cd lambda && find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	@cd lambda && rm -rf bin/ 2>/dev/null || true
	@echo "Cleanup complete."
