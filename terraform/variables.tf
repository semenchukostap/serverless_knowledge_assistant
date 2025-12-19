variable "aws_region" {
  description = "AWS region where resources will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as prefix for resource naming"
  type        = string
  default     = "knowledge-assistant"
}

variable "bedrock_model_id" {
  description = "Amazon Bedrock Nova model ID for text generation (e.g., amazon.nova-pro-v1:0 or amazon.nova-micro-v1:0)"
  type        = string
  default     = "amazon.nova-micro-v1:0"
}
