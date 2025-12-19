resource "aws_lambda_function" "knowledge_assistant" {
  filename         = "${path.module}/../build/lambda_package.zip"
  function_name    = "${var.project_name}-function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 12
  source_code_hash = try(filebase64sha256("${path.module}/../build/lambda_package.zip"), "")

  environment {
    variables = {
      LOG_LEVEL        = "INFO"
      BEDROCK_KB_ID    = aws_bedrockagent_knowledge_base.kb.id
      BEDROCK_MODEL_ID = var.bedrock_model_id
    }
  }

  tags = {
    Name        = "Knowledge Assistant Lambda"
    Environment = "PoC"
  }

  depends_on = [
    aws_bedrockagent_knowledge_base.kb
  ]
}
