"""Unit tests for Lambda handler."""

import json
from unittest.mock import patch

from handler import lambda_handler


def test_successful_query(api_gateway_event_base, mock_lambda_context, sample_query_request):
    """Test successful query processing."""
    event = api_gateway_event_base.copy()
    event["body"] = json.dumps(sample_query_request)

    with patch("handler.generate_text_from_kb", return_value="Test answer"):
        response = lambda_handler(event, mock_lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["answer"] == "Test answer"


def test_invalid_method_returns_400(api_gateway_event_base, mock_lambda_context):
    """Test that non-POST methods return 400."""
    event = api_gateway_event_base.copy()
    event["requestContext"]["http"]["method"] = "GET"

    response = lambda_handler(event, mock_lambda_context)
    assert response["statusCode"] == 400


def test_empty_body_returns_400(api_gateway_event_base, mock_lambda_context):
    """Test that empty body returns 400."""
    event = api_gateway_event_base.copy()
    event["body"] = ""

    response = lambda_handler(event, mock_lambda_context)
    assert response["statusCode"] == 400


def test_invalid_json_returns_400(api_gateway_event_base, mock_lambda_context):
    """Test that invalid JSON returns 400."""
    event = api_gateway_event_base.copy()
    event["body"] = "{ invalid json }"

    response = lambda_handler(event, mock_lambda_context)
    assert response["statusCode"] == 400


def test_bedrock_error_returns_500(
    api_gateway_event_base, mock_lambda_context, sample_query_request
):
    """Test that Bedrock errors return 500."""
    event = api_gateway_event_base.copy()
    event["body"] = json.dumps(sample_query_request)

    with patch("handler.generate_text_from_kb", side_effect=RuntimeError("Bedrock error")):
        response = lambda_handler(event, mock_lambda_context)

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
