variable "s3_bucket_lambda_package" {
  type = string
}

variable "wrangler_layer" {
  type    = string
  default = "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python310:10"
}