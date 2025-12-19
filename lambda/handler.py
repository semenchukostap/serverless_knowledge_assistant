"""Lambda handler for API Gateway POST /query endpoint."""

import base64
import json
import logging
from typing import Any

from bedrock_client import generate_text_from_kb
from pydantic import ValidationError
from schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Process POST requests to /query endpoint.

    Validates input, calls Bedrock KB, and returns JSON response with proper status codes.
    """
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
    }

    try:
        request_context = event.get("requestContext", {})
        http_info = request_context.get("http", {})
        http_method = http_info.get("method", "").upper()

        if not http_method:
            http_method = event.get("httpMethod", "").upper()

        if http_method != "POST":
            logger.warning(f"Invalid HTTP method: {http_method}")
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps(
                    {"error": f"Method not allowed. Expected POST, got {http_method}"}
                ),
            }

        body_str = event.get("body", "")

        if event.get("isBase64Encoded", False):
            body_str = base64.b64decode(body_str).decode("utf-8")
        if not body_str:
            logger.warning("Empty request body")
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps(
                    {"error": "Request body is required and must contain a 'query' field"}
                ),
            }

        try:
            body_json = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON: {e}")
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": f"Invalid JSON format: {str(e)}"}),
            }

        try:
            request = QueryRequest(**body_json)
        except ValidationError as e:
            error_messages = [err["msg"] for err in e.errors()]
            logger.warning(f"Validation error: {error_messages}")
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Invalid request format", "details": error_messages}),
            }

        query = request.query
        logger.info(f"Processing query: {query[:100]}...")
        answer = generate_text_from_kb(query)

        response = QueryResponse(answer=answer)
        logger.info("Successfully generated answer")
        return {"statusCode": 200, "headers": headers, "body": response.model_dump_json()}

    except ValueError as e:
        logger.error(f"Value error: {e}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Configuration error", "message": str(e)}),
        }

    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps(
                {"error": "Failed to generate answer from knowledge base", "message": str(e)}
            ),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred while processing your request",
                }
            ),
        }
