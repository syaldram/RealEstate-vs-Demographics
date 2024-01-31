terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "> 4.0"
    }
    archive = {
      source = "hashicorp/archive"
    }
  }
  backend "s3" {
    bucket         = "terraform-backend-sy"
    key            = "real_estate_demographics.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Project     = "Data Science and Dataframes"
      Provisioned = "Terraform"
      Owner       = "Saad Yaldram"
    }
  }
}