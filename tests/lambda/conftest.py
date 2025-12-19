"""Pytest configuration and shared fixtures."""

from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_lambda_context() -> Any:
    """Mock Lambda context object."""
    context = MagicMock()
    context.function_name = "test-function"
    context.memory_limit_in_mb = 128
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    context.aws_request_id = "test-request-id"
    return context


@pytest.fixture
def api_gateway_event_base() -> dict[str, Any]:
    """Base API Gateway HTTP API v2 event structure."""
    return {
        "version": "2.0",
        "routeKey": "POST /query",
        "rawPath": "/query",
        "rawQueryString": "",
        "headers": {
            "content-type": "application/json",
        },
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/query",
                "protocol": "HTTP/1.1",
            },
            "requestId": "test-request-id",
            "time": "01/Jan/2024:00:00:00 +0000",
        },
        "body": "",
        "isBase64Encoded": False,
    }


@pytest.fixture
def sample_query_request() -> dict[str, Any]:
    """Sample valid query request body."""
    return {"query": "What are the key principles of serverless architecture?"}


@pytest.fixture(autouse=True)
def reset_bedrock_clients(monkeypatch: pytest.MonkeyPatch):
    """Reset bedrock clients before each test to ensure clean state."""
    import bedrock_client

    bedrock_client._bedrock_agent_runtime_client = None
    bedrock_client._bedrock_runtime_client = None
    yield
    # Cleanup after test
    bedrock_client._bedrock_agent_runtime_client = None
    bedrock_client._bedrock_runtime_client = None
