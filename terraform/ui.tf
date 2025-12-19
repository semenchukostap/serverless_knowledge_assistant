resource "aws_s3_bucket" "ui" {
  bucket_prefix = "${var.project_name}-ui-"

  tags = {
    Name        = "Knowledge Assistant UI"
    Environment = "PoC"
  }
}

resource "aws_s3_bucket_website_configuration" "ui" {
  bucket = aws_s3_bucket.ui.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "ui" {
  bucket = aws_s3_bucket.ui.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "ui" {
  bucket = aws_s3_bucket.ui.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.ui.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.ui]
}

resource "aws_s3_object" "ui_index" {
  bucket       = aws_s3_bucket.ui.id
  key          = "index.html"
  content      = templatefile("${path.module}/../ui/index.html", {
    api_gateway_query_endpoint = "${aws_apigatewayv2_api.api.api_endpoint}/query"
  })
  content_type = "text/html"

  depends_on = [
    aws_s3_bucket_website_configuration.ui,
    aws_apigatewayv2_api.api
  ]

  tags = {
    Name        = "UI Index"
    Environment = "PoC"
  }
}

resource "aws_s3_object" "ui_styles" {
  bucket       = aws_s3_bucket.ui.id
  key          = "styles.css"
  source       = "${path.module}/../ui/styles.css"
  content_type = "text/css"

  depends_on = [
    aws_s3_bucket_website_configuration.ui
  ]

  tags = {
    Name        = "UI Styles"
    Environment = "PoC"
  }
}

