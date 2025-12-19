"""Unit tests for Bedrock client."""

import json
from unittest.mock import MagicMock, patch

import bedrock_client
import pytest
from botocore.exceptions import ClientError


@patch.dict(
    "os.environ",
    {"BEDROCK_KB_ID": "test-kb-id", "BEDROCK_MODEL_ID": "amazon.nova-micro-v1:0"},
)
def test_successful_generation(monkeypatch):
    """Test successful text generation."""
    mock_retrieve_response = {
        "retrievalResults": [{"content": {"text": "Context about serverless"}, "score": 0.95}]
    }

    mock_model_response = {
        "output": {
            "message": {
                "content": [{"text": "Serverless architecture is a cloud computing model..."}],
                "role": "assistant",
            }
        },
        "stopReason": "end_turn",
    }

    mock_agent_client = MagicMock()
    mock_agent_client.retrieve.return_value = mock_retrieve_response

    mock_runtime_client = MagicMock()
    mock_body = MagicMock()
    mock_body.read.return_value = json.dumps(mock_model_response).encode("utf-8")
    mock_runtime_client.invoke_model.return_value = {"body": mock_body}

    monkeypatch.setattr(bedrock_client, "_bedrock_agent_runtime_client", mock_agent_client)
    monkeypatch.setattr(bedrock_client, "_bedrock_runtime_client", mock_runtime_client)

    result = bedrock_client.generate_text_from_kb("What is serverless?")
    assert "Serverless architecture" in result

    # Verify that Nova API format was used (messages with content array, inferenceConfig)
    call_args = mock_runtime_client.invoke_model.call_args
    assert call_args is not None
    body_json = json.loads(call_args.kwargs["body"])
    assert "messages" in body_json
    assert "inferenceConfig" in body_json
    assert body_json["inferenceConfig"]["maxTokens"] == 1024
    assert isinstance(body_json["messages"][0]["content"], list)
    assert call_args.kwargs["modelId"] == "amazon.nova-micro-v1:0"


def test_empty_query_raises_error():
    """Test that empty query raises ValueError."""
    with pytest.raises(ValueError, match="Query must be a non-empty string"):
        bedrock_client.generate_text_from_kb("")


@patch.dict("os.environ", {}, clear=True)
def test_missing_kb_id_raises_error():
    """Test that missing BEDROCK_KB_ID raises ValueError."""
    with pytest.raises(ValueError, match="BEDROCK_KB_ID is not configured"):
        bedrock_client.generate_text_from_kb("test query")


@patch.dict(
    "os.environ",
    {"BEDROCK_KB_ID": "test-kb-id", "BEDROCK_MODEL_ID": "amazon.nova-micro-v1:0"},
)
def test_empty_retrieval_results_returns_fallback(monkeypatch):
    """Test that empty retrieval results return fallback message."""
    mock_retrieve_response = {"retrievalResults": []}

    mock_agent_client = MagicMock()
    mock_agent_client.retrieve.return_value = mock_retrieve_response

    monkeypatch.setattr(bedrock_client, "_bedrock_agent_runtime_client", mock_agent_client)

    result = bedrock_client.generate_text_from_kb("test query")
    assert "couldn't find relevant information" in result.lower()


@patch.dict(
    "os.environ",
    {"BEDROCK_KB_ID": "test-kb-id", "BEDROCK_MODEL_ID": "amazon.nova-micro-v1:0"},
)
def test_client_error_raises_runtime_error(monkeypatch):
    """Test that ClientError from Bedrock raises RuntimeError."""
    mock_agent_client = MagicMock()
    error_response = {
        "Error": {"Code": "ValidationException", "Message": "Invalid knowledge base ID"}
    }
    mock_agent_client.retrieve.side_effect = ClientError(error_response, "retrieve")

    monkeypatch.setattr(bedrock_client, "_bedrock_agent_runtime_client", mock_agent_client)

    with pytest.raises(RuntimeError, match="Failed to generate answer"):
        bedrock_client.generate_text_from_kb("test query")
