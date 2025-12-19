output "s3_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  value       = aws_s3_bucket.documents.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for document storage"
  value       = aws_s3_bucket.documents.arn
}

output "lambda_role_name" {
  description = "Name of the IAM role for Lambda execution"
  value       = aws_iam_role.lambda_role.name
}

output "lambda_role_arn" {
  description = "ARN of the IAM role for Lambda execution"
  value       = aws_iam_role.lambda_role.arn
}

output "lambda_policy_name" {
  description = "Name of the IAM policy attached to Lambda role"
  value       = aws_iam_policy.lambda_policy.name
}

output "lambda_policy_arn" {
  description = "ARN of the IAM policy attached to Lambda role"
  value       = aws_iam_policy.lambda_policy.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.knowledge_assistant.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.knowledge_assistant.arn
}

output "lambda_function_invoke_arn" {
  description = "ARN to invoke the Lambda function"
  value       = aws_lambda_function.knowledge_assistant.invoke_arn
}

output "api_gateway_url" {
  description = "URL of the API Gateway HTTP API endpoint"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "api_gateway_query_endpoint" {
  description = "Full URL for the POST /query endpoint"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/query"
}

output "bedrock_embedding_model_id" {
  description = "Bedrock foundation model ID for embeddings (Amazon Titan)"
  value       = local.bedrock_embedding_model_id
}

output "bedrock_embedding_model_arn" {
  description = "ARN of the Bedrock foundation model for embeddings"
  value       = local.bedrock_embedding_model_arn
}

output "bedrock_text_model_id" {
  description = "Bedrock foundation model ID for text generation (Nova Micro/Pro)"
  value       = local.bedrock_text_model_id
}

output "bedrock_text_model_arn" {
  description = "ARN of the Bedrock foundation model for text generation"
  value       = local.bedrock_text_model_arn
}

output "bedrock_knowledge_base_id" {
  description = "ID of the Amazon Bedrock Knowledge Base"
  value       = aws_bedrockagent_knowledge_base.kb.id
}

output "bedrock_knowledge_base_arn" {
  description = "ARN of the Amazon Bedrock Knowledge Base"
  value       = aws_bedrockagent_knowledge_base.kb.arn
}

output "bedrock_kb_role_arn" {
  description = "ARN of the IAM role for Bedrock Knowledge Base service"
  value       = aws_iam_role.bedrock_kb_role.arn
}

output "bedrock_s3_bucket_arn" {
  description = "ARN of the S3 bucket for document ingestion (for KB configuration)"
  value       = aws_s3_bucket.documents.arn
}

output "vector_store_bucket_name" {
  description = "Name of the S3 Vectors bucket used for vector storage"
  value       = aws_s3vectors_vector_bucket.vector_store.vector_bucket_name
}

output "vector_store_bucket_arn" {
  description = "ARN of the S3 Vectors bucket used for vector storage"
  value       = aws_s3vectors_vector_bucket.vector_store.vector_bucket_arn
}

output "bedrock_data_source_id" {
  description = "ID of the Bedrock Knowledge Base data source"
  value       = aws_bedrockagent_data_source.s3_documents.data_source_id
}

output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "ui_bucket_name" {
  description = "Name of the S3 bucket for UI static website hosting"
  value       = aws_s3_bucket.ui.id
}

output "ui_bucket_arn" {
  description = "ARN of the S3 bucket for UI static website hosting"
  value       = aws_s3_bucket.ui.arn
}

output "ui_website_url" {
  description = "Public URL of the S3 static website"
  value       = "http://${aws_s3_bucket_website_configuration.ui.website_endpoint}"
}

