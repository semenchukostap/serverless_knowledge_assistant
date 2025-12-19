data "aws_caller_identity" "current" {}
locals {
  bedrock_embedding_model_id  = "amazon.titan-embed-text-v1"
  bedrock_embedding_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/${local.bedrock_embedding_model_id}"

  bedrock_text_model_id  = var.bedrock_model_id
  bedrock_text_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"

  common_tags = {
    Name        = "Knowledge Assistant"
    Environment = "PoC"
  }
}

resource "aws_iam_role" "bedrock_kb_role" {
  name = "${var.project_name}-bedrock-kb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "bedrock.amazonaws.com"
      }
      Action = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })

  tags = merge(local.common_tags, {
    Name = "Bedrock Knowledge Base Service Role"
  })
}

resource "aws_iam_policy" "bedrock_kb_policy" {
  name        = "${var.project_name}-bedrock-kb-policy"
  description = "Least-privilege policy: S3 read (source) + S3 read/write (vectors) + Bedrock invoke"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3ReadAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
      },
      {
        Sid    = "AllowS3VectorStoreAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3vectors_vector_bucket.vector_store.vector_bucket_arn,
          "${aws_s3vectors_vector_bucket.vector_store.vector_bucket_arn}/*"
        ]
      },
      {
        Sid    = "AllowBedrockInvoke"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [local.bedrock_embedding_model_arn]
      },
      {
        Sid    = "AllowS3VectorsAccess"
        Effect = "Allow"
        Action = [
          "s3vectors:QueryVectors",
          "s3vectors:PutVectors",
          "s3vectors:DeleteVectors",
          "s3vectors:GetVectors"
        ]
        Resource = [
          aws_s3vectors_vector_bucket.vector_store.vector_bucket_arn,
          "${aws_s3vectors_vector_bucket.vector_store.vector_bucket_arn}/*",
          aws_s3vectors_index.vector_index.index_arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_kb_policy_attachment" {
  role       = aws_iam_role.bedrock_kb_role.name
  policy_arn = aws_iam_policy.bedrock_kb_policy.arn
}

# S3 Vectors vector bucket (special bucket type for S3 Vectors)
resource "aws_s3vectors_vector_bucket" "vector_store" {
  vector_bucket_name = "${var.project_name}-vectors"
}

# S3 Vectors index for Bedrock Knowledge Base
# Titan Embed Text v1 produces 1536-dimensional vectors
resource "aws_s3vectors_index" "vector_index" {
  vector_bucket_name = aws_s3vectors_vector_bucket.vector_store.vector_bucket_name
  index_name         = "${var.project_name}-index"
  data_type          = "float32"
  dimension          = 1536
  distance_metric    = "cosine"

  # Mark Bedrock-generated metadata fields as non-filterable to avoid 2048 byte limit
  metadata_configuration {
    non_filterable_metadata_keys = [
      "AMAZON_BEDROCK_TEXT",
      "AMAZON_BEDROCK_METADATA",
      "text",
      "chunk",
      "content",
      "body",
      "document",
      "source_metadata",
      "metadata",
      "page_content"
    ]
  }
}

resource "aws_bedrockagent_knowledge_base" "kb" {
  name     = "${var.project_name}-kb"
  role_arn = aws_iam_role.bedrock_kb_role.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = local.bedrock_embedding_model_arn
    }
  }

  storage_configuration {
    type = "S3_VECTORS"
    s3_vectors_configuration {
      index_arn = aws_s3vectors_index.vector_index.index_arn
    }
  }

  tags = merge(local.common_tags, {
    Name = "Knowledge Assistant Knowledge Base"
  })
}

resource "aws_bedrockagent_data_source" "s3_documents" {
  name              = "${var.project_name}-s3-documents"
  knowledge_base_id = aws_bedrockagent_knowledge_base.kb.id

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.documents.arn
    }
  }
}
