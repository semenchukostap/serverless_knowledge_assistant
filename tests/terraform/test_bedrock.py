"""Tests for Bedrock Knowledge Base infrastructure."""

from .utils import extract_role_name_from_arn, get_terraform_output


def test_bedrock_knowledge_base_exists(terraform_outputs, bedrock_client):
    """Test that Bedrock Knowledge Base exists and is active."""
    kb_id = get_terraform_output(terraform_outputs, "bedrock_knowledge_base_id")

    response = bedrock_client.get_knowledge_base(knowledgeBaseId=kb_id)
    kb = response["knowledgeBase"]

    assert kb["knowledgeBaseId"] == kb_id
    assert kb["status"] == "ACTIVE"


def test_bedrock_data_source_exists(terraform_outputs, bedrock_client):
    """Test that Bedrock data source exists and is available."""
    kb_id = get_terraform_output(terraform_outputs, "bedrock_knowledge_base_id")
    data_source_id = get_terraform_output(terraform_outputs, "bedrock_data_source_id")

    response = bedrock_client.get_data_source(knowledgeBaseId=kb_id, dataSourceId=data_source_id)
    data_source = response["dataSource"]

    assert data_source["dataSourceId"] == data_source_id
    assert data_source["status"] == "AVAILABLE"


def test_bedrock_kb_role_exists(terraform_outputs, iam_client):
    """Test that Bedrock Knowledge Base role exists."""
    role_arn = get_terraform_output(terraform_outputs, "bedrock_kb_role_arn")
    role_name = extract_role_name_from_arn(role_arn)

    response = iam_client.get_role(RoleName=role_name)

    assert response["Role"]["Arn"] == role_arn
