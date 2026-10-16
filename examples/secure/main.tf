terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# This is an example configuration for scanning/validation only.
# No resources are created unless someone explicitly runs terraform apply.
provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "patient_documents_demo" {
  bucket_prefix = "healthcare-documents-demo-"
  # Do not store real patient information in this learning project.
}

resource "aws_s3_bucket_public_access_block" "patient_documents_demo" {
  bucket                  = aws_s3_bucket.patient_documents_demo.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "patient_documents_demo" {
  bucket = aws_s3_bucket.patient_documents_demo.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "patient_documents_demo" {
  bucket = aws_s3_bucket.patient_documents_demo.id

  versioning_configuration {
    status = "Enabled"
  }
}
