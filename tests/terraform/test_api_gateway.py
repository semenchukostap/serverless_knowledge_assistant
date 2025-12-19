"""Tests for API Gateway infrastructure."""

from .utils import extract_api_id_from_url, get_terraform_output


def test_api_gateway_exists(terraform_outputs, apigateway_client):
    """Test that API Gateway HTTP API exists."""
    api_url = get_terraform_output(terraform_outputs, "api_gateway_url")
    api_id = extract_api_id_from_url(api_url)

    response = apigateway_client.get_api(ApiId=api_id)

    assert response["ApiId"] == api_id
    assert response["ProtocolType"] == "HTTP"


def test_api_gateway_has_query_route(terraform_outputs, apigateway_client):
    """Test that API Gateway has /query route configured."""
    api_url = get_terraform_output(terraform_outputs, "api_gateway_url")
    api_id = extract_api_id_from_url(api_url)

    routes = apigateway_client.get_routes(ApiId=api_id)
    route_keys = [route["RouteKey"] for route in routes["Items"]]

    assert "POST /query" in route_keys
