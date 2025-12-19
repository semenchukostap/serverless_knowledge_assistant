"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from schemas import QueryRequest, QueryResponse


def test_query_request_valid():
    """Test valid query request."""
    request = QueryRequest(query="What is serverless?")
    assert request.query == "What is serverless?"


def test_query_request_empty_raises_error():
    """Test that empty string raises ValidationError."""
    with pytest.raises(ValidationError):
        QueryRequest(query="")


def test_query_request_missing_field_raises_error():
    """Test that missing query field raises ValidationError."""
    with pytest.raises(ValidationError):
        QueryRequest()


def test_query_response_valid():
    """Test valid query response."""
    response = QueryResponse(answer="Serverless is a cloud computing model...")
    assert response.answer == "Serverless is a cloud computing model..."


def test_query_response_empty_raises_error():
    """Test that empty string raises ValidationError."""
    with pytest.raises(ValidationError):
        QueryResponse(answer="")
