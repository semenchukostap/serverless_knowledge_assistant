"""Helper utilities for infrastructure tests."""

from typing import Any


def get_terraform_output(terraform_outputs: dict[str, Any], key: str) -> str:
    """Get Terraform output value by key."""
    return terraform_outputs[key]["value"]


def extract_api_id_from_url(api_url: str) -> str:
    """Extract API Gateway API ID from URL."""
    return api_url.split("//")[1].split(".")[0]


def extract_role_name_from_arn(role_arn: str) -> str:
    """Extract IAM role name from ARN."""
    return role_arn.split("/")[-1]
