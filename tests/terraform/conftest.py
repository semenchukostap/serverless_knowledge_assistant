"""Pytest fixtures for infrastructure tests."""

import json
import subprocess
from pathlib import Path
from typing import Any

import boto3
import pytest


@pytest.fixture(scope="session")
def terraform_outputs() -> dict[str, Any]:
    """Get Terraform outputs as a dictionary."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    terraform_dir = project_root / "terraform"

    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=str(terraform_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        pytest.skip(f"Could not get Terraform outputs: {e}")


@pytest.fixture(scope="session")
def aws_region(terraform_outputs: dict[str, Any]) -> str:
    """Get AWS region from Terraform outputs."""
    return terraform_outputs.get("aws_region", {}).get("value", "us-east-1")


@pytest.fixture(scope="session")
def lambda_client(aws_region: str):
    """Create boto3 Lambda client."""
    return boto3.client("lambda", region_name=aws_region)


@pytest.fixture(scope="session")
def s3_client(aws_region: str):
    """Create boto3 S3 client."""
    return boto3.client("s3", region_name=aws_region)


@pytest.fixture(scope="session")
def apigateway_client(aws_region: str):
    """Create boto3 API Gateway client."""
    return boto3.client("apigatewayv2", region_name=aws_region)


@pytest.fixture(scope="session")
def bedrock_client(aws_region: str):
    """Create boto3 Bedrock Agent client."""
    return boto3.client("bedrock-agent", region_name=aws_region)


@pytest.fixture(scope="session")
def iam_client(aws_region: str):
    """Create boto3 IAM client."""
    return boto3.client("iam", region_name=aws_region)
