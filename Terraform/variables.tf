variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket that hosts the static site."
}

variable "domain_name" {
  type        = string
  description = "Fully-qualified domain name served by CloudFront (e.g. data.saadyaldram.com)."
}

variable "hosted_zone_name" {
  type        = string
  description = "Route53 hosted zone name without trailing dot (e.g. saadyaldram.com)."
}

variable "certificate_arn" {
  type        = string
  description = "ARN of the ACM certificate in us-east-1 covering var.domain_name."
}

variable "github_repo" {
  type        = string
  description = "GitHub repo in <owner>/<name> form, used to scope the OIDC trust policy."
}
