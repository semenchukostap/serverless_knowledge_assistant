resource "aws_s3_bucket" "documents" {
  bucket_prefix = "${var.project_name}-documents-"

  tags = {
    Name        = "Knowledge Assistant Documents"
    Environment = "PoC"
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "lambda_read_only" {
  bucket = aws_s3_bucket.documents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowLambdaReadOnly"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.lambda_role.arn
        }
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.documents]
}

resource "aws_s3_object" "wellarchitected_pdf" {
  bucket = aws_s3_bucket.documents.id
  key    = "wellarchitected-serverless-applications-lens.pdf"
  source = "${path.module}/../knowledge-base/wellarchitected-serverless-applications-lens.pdf"

  depends_on = [
    aws_s3_bucket_server_side_encryption_configuration.documents,
    aws_s3_bucket_versioning.documents
  ]

  tags = {
    Name        = "AWS Serverless Application Lens"
    Environment = "PoC"
  }
}

