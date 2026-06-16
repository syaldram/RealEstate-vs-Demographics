output "bucket_name" {
  value       = aws_s3_bucket.site.bucket
  description = "S3 bucket hosting the static site."
}

output "cloudfront_distribution_id" {
  value       = aws_cloudfront_distribution.site.id
  description = "CloudFront distribution ID (use for cache invalidations)."
}

output "cloudfront_domain_name" {
  value       = aws_cloudfront_distribution.site.domain_name
  description = "CloudFront default domain, useful for verification before DNS propagates."
}

output "site_url" {
  value       = "https://${var.domain_name}"
  description = "Public URL of the static site."
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions_deploy.arn
  description = "Role ARN GitHub Actions assumes via OIDC for deploys."
}
