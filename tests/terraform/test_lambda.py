"""Tests for Lambda function infrastructure."""

import json

from .utils import extract_role_name_from_arn, get_terraform_output


def test_lambda_function_exists(terraform_outputs, lambda_client):
    """Test that Lambda function exists and is accessible."""
    function_name = get_terraform_output(terraform_outputs, "lambda_function_name")

    response = lambda_client.get_function(FunctionName=function_name)
    config = response["Configuration"]

    assert config["FunctionName"] == function_name
    assert config["Runtime"] == "python3.11"
    assert config["Handler"] == "handler.lambda_handler"
    assert config["Timeout"] == 12


def test_lambda_function_has_environment_variables(terraform_outputs, lambda_client):
    """Test that Lambda function has required environment variables."""
    function_name = get_terraform_output(terraform_outputs, "lambda_function_name")

    response = lambda_client.get_function_configuration(FunctionName=function_name)
    env_vars = response.get("Environment", {}).get("Variables", {})

    required_vars = ["BEDROCK_KB_ID", "BEDROCK_MODEL_ID", "LOG_LEVEL"]
    for var in required_vars:
        assert var in env_vars, f"Missing environment variable: {var}"


def test_lambda_function_role_exists(terraform_outputs, iam_client):
    """Test that Lambda execution role exists with correct trust policy."""
    role_arn = get_terraform_output(terraform_outputs, "lambda_role_arn")
    role_name = extract_role_name_from_arn(role_arn)

    response = iam_client.get_role(RoleName=role_name)
    role = response["Role"]

    assert role["Arn"] == role_arn

    # Verify trust policy allows Lambda service
    policy_doc = role["AssumeRolePolicyDocument"]
    if isinstance(policy_doc, str):
        policy_doc = json.loads(policy_doc)

    principal_service = policy_doc["Statement"][0]["Principal"]["Service"]
    assert principal_service == "lambda.amazonaws.com"
