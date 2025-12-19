"""Pydantic schemas for API Gateway request and response validation."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema with query field for Knowledge Assistant queries."""

    query: str = Field(..., min_length=1, description="User's question or query string")


class QueryResponse(BaseModel):
    """Response schema with answer field from Bedrock Knowledge Base."""

    answer: str = Field(..., min_length=1, description="Generated answer from knowledge base")
