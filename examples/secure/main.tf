terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for the educational example."
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Replace this placeholder with a globally unique S3 bucket name before any real deployment."
  type        = string
  default     = "replace-with-unique-healthcare-demo-bucket"

  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63
    error_message = "The S3 bucket name must be between 3 and 63 characters."
  }
}

variable "log_bucket_name" {
  description = "Replace this placeholder with a different globally unique S3 bucket name before any real deployment."
  type        = string
  default     = "replace-with-unique-healthcare-demo-logs"

  validation {
    condition     = length(var.log_bucket_name) >= 3 && length(var.log_bucket_name) <= 63
    error_message = "The S3 log bucket name must be between 3 and 63 characters."
  }
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "healthcare_data" {
  description             = "Customer-managed KMS key for the healthcare demo data bucket"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  tags = {
    Project     = "healthcare-devsecops-demo"
    Environment = "demo"
  }
}

resource "aws_s3_bucket" "healthcare_data" {
  bucket        = var.bucket_name
  force_destroy = false

  tags = {
    Name                = "healthcare-demo-data"
    DataClassification  = "SensitiveDemoOnly"
    Environment         = "demo"
    Project             = "healthcare-devsecops-demo"
  }
}

resource "aws_s3_bucket_public_access_block" "healthcare_data" {
  bucket                  = aws_s3_bucket.healthcare_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "healthcare_data" {
  bucket = aws_s3_bucket.healthcare_data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "healthcare_data" {
  bucket = aws_s3_bucket.healthcare_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "healthcare_data" {
  bucket = aws_s3_bucket.healthcare_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.healthcare_data.arn
    }

    bucket_key_enabled = true
  }
}

# Dedicated destination for S3 server access logs.
# AWS requires this destination to use SSE-S3 rather than SSE-KMS.
resource "aws_s3_bucket" "access_logs" {
  #checkov:skip=CKV_AWS_18:This is the terminal access-log destination; logging it to itself would create recursive logging.
  #checkov:skip=CKV_AWS_145:AWS S3 server access logging destinations must use SSE-S3; SSE-KMS is not supported for this destination.
  bucket        = var.log_bucket_name
  force_destroy = false

  tags = {
    Name        = "healthcare-demo-access-logs"
    Environment = "demo"
    Project     = "healthcare-devsecops-demo"
  }
}

resource "aws_s3_bucket_public_access_block" "access_logs" {
  bucket                  = aws_s3_bucket.access_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowS3ServerAccessLogging"
        Effect    = "Allow"
        Principal = { Service = "logging.s3.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.access_logs.arn}/*"
        Condition = {
          ArnLike      = { "aws:SourceArn" = aws_s3_bucket.healthcare_data.arn }
          StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
        }
      },
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.access_logs.arn,
          "${aws_s3_bucket.access_logs.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_logging" "healthcare_data" {
  bucket        = aws_s3_bucket.healthcare_data.id
  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "healthcare-data/"

  depends_on = [aws_s3_bucket_policy.access_logs]
}

resource "aws_s3_bucket_policy" "healthcare_data" {
  bucket = aws_s3_bucket.healthcare_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.healthcare_data.arn,
          "${aws_s3_bucket.healthcare_data.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}
