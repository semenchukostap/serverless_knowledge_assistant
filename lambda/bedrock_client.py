"""Bedrock client for RAG operations using Knowledge Base."""

import json
import logging
import os
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Module-level clients for runtime (can be overridden in tests)
_bedrock_agent_runtime_client: Any | None = None
_bedrock_runtime_client: Any | None = None


def _get_bedrock_agent_runtime_client():
    """Get or create bedrock-agent-runtime client. Allows injection for testing."""
    global _bedrock_agent_runtime_client
    if _bedrock_agent_runtime_client is None:
        _bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime")
    return _bedrock_agent_runtime_client


def _get_bedrock_runtime_client():
    """Get or create bedrock-runtime client. Allows injection for testing."""
    global _bedrock_runtime_client
    if _bedrock_runtime_client is None:
        _bedrock_runtime_client = boto3.client("bedrock-runtime")
    return _bedrock_runtime_client


def _get_bedrock_kb_id() -> str:
    """Get Bedrock Knowledge Base ID from environment. Allows override for testing."""
    return os.getenv("BEDROCK_KB_ID", "")


def _get_bedrock_model_id() -> str:
    """Get Bedrock Model ID from environment. Allows override for testing."""
    return os.getenv("BEDROCK_MODEL_ID", "")


def generate_text_from_kb(query: str) -> str:
    """
    Generate answer from Bedrock Knowledge Base using RAG with Nova models.

    Supports Nova Pro (amazon.nova-pro-v1:0) and Nova Micro (amazon.nova-micro-v1:0).
    Retrieves context from KB and invokes Nova model to generate answer.
    Returns only the answer text string.
    """
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string")

    bedrock_kb_id = _get_bedrock_kb_id()
    bedrock_model_id = _get_bedrock_model_id()

    if not bedrock_kb_id:
        raise ValueError("BEDROCK_KB_ID is not configured")

    if not bedrock_model_id:
        raise ValueError("BEDROCK_MODEL_ID is not configured")

    try:
        logger.info(f"Retrieving context for query: {query[:50]}...")
        retrieved_context = _retrieve_from_kb(query, bedrock_kb_id)

        valid_context = [
            result
            for result in retrieved_context
            if result.get("content", {}).get("text", "").strip()
        ]

        if not valid_context:
            logger.warning(
                f"No valid context retrieved (got {len(retrieved_context)} results, "
                f"{len(valid_context)} with text)"
            )
            return (
                "I couldn't find relevant information in the knowledge base to answer your query."
            )

        logger.info(f"Generating answer using foundation model: {bedrock_model_id}")
        answer = _invoke_model_with_context(query, valid_context, bedrock_model_id)
        return answer

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"Bedrock API error ({error_code}): {error_message}")
        raise RuntimeError(f"Failed to generate answer: {error_message}") from e

    except BotoCoreError as e:
        logger.error(f"Boto3 client error: {e}")
        raise RuntimeError(f"Error connecting to Bedrock: {e}") from e

    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Unexpected response format: {e}")
        raise RuntimeError(f"Unexpected response format: {e}") from e


def _retrieve_from_kb(query: str, bedrock_kb_id: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Retrieve relevant context chunks from Knowledge Base."""
    try:
        client = _get_bedrock_agent_runtime_client()
        response = client.retrieve(
            knowledgeBaseId=bedrock_kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": max_results}},
        )

        results = response.get("retrievalResults", [])
        logger.info(f"Retrieved {len(results)} results from Knowledge Base")

        if not results:
            logger.warning("Retrieval returned empty results list")

        return results
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"Error retrieving from KB ({error_code}): {error_message}")
        raise


def _invoke_model_with_context(
    query: str, context: list[dict[str, Any]], bedrock_model_id: str
) -> str:
    """Invoke foundation model with query and retrieved context to generate answer."""
    context_text = "\n\n".join(
        [
            result.get("content", {}).get("text", "")
            for result in context
            if result.get("content", {}).get("text")
        ]
    )

    # Nova models (Pro and Micro) use messages API format with content as array
    prompt = f"""Use the following pieces of context to answer the question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context_text}

Question: {query}

Answer:"""

    body = {
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {
            "maxTokens": 1024,
            "temperature": 0.7,
        },
    }

    logger.info(f"Invoking foundation model: {bedrock_model_id}")
    client = _get_bedrock_runtime_client()
    response = client.invoke_model(
        modelId=bedrock_model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    response_body = json.loads(response["body"].read().decode("utf-8"))
    logger.debug(f"Response body keys: {list(response_body.keys())}")

    # Nova models (Pro and Micro) use output.message.content structure
    output = response_body.get("output", {})
    message = output.get("message", {})
    content = message.get("content", [])

    if content and isinstance(content, list) and len(content) > 0:
        answer = content[0].get("text", "")
    else:
        logger.error(f"Unexpected foundation model response format: {response_body}")
        raise KeyError("Could not extract answer from foundation model response")

    if not answer or not answer.strip():
        raise KeyError("Empty answer received from foundation model")

    return answer.strip()
