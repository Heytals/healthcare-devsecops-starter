terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

# INTENTIONALLY INSECURE TRAINING EXAMPLE — NEVER APPLY THIS CONFIGURATION.
# Public ACL and missing encryption/public-access protections illustrate a bad configuration.
resource "aws_s3_bucket" "patient_documents_demo_insecure" {
  bucket_prefix = "insecure-healthcare-demo-"
  acl           = "public-read"
}
