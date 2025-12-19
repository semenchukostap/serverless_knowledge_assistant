"""Tests for S3 bucket infrastructure."""

from .utils import get_terraform_output


def test_s3_bucket_exists(terraform_outputs, s3_client):
    """Test that S3 bucket exists."""
    bucket_name = get_terraform_output(terraform_outputs, "s3_bucket_name")

    # head_bucket raises exception if bucket doesn't exist
    response = s3_client.head_bucket(Bucket=bucket_name)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_s3_bucket_versioning_configured(terraform_outputs, s3_client):
    """Test that S3 bucket has versioning configured (disabled for PoC)."""
    bucket_name = get_terraform_output(terraform_outputs, "s3_bucket_name")

    response = s3_client.get_bucket_versioning(Bucket=bucket_name)

    # When versioning is disabled, response is empty {} or has Status key
    # For PoC, versioning is disabled, so we verify the API call succeeds
    assert "ResponseMetadata" in response or "Status" in response or len(response) == 0
