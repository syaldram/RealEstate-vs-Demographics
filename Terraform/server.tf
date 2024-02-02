data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

################################################################################
# Lambda function to host serverless application
################################################################################

module "flask_app" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name  = "real_estate_demographics"
  description    = "Serverless application called Real Estate vs Demographics"
  handler        = "app.lambda_handler"
  runtime        = "python3.10"
  create_package = true
  timeout        = 600
  memory_size    = 512
  publish        = true

  source_path = [{
    path             = "${path.module}./app"
    pip_requirements = "${path.module}./app/requirements.txt"
    patterns         = ["!\\.env", "!test_.*\\.py", "!conftest\\.py", "!__pycache__/.*"]
  }]

  build_in_docker          = true
  docker_build_root        = "${path.module}./app/docker"
  docker_image             = "public.ecr.aws/lambda/python:3.10"
  store_on_s3              = true
  s3_bucket                = var.s3_bucket_lambda_package
  recreate_missing_package = true

  create_role = false
  lambda_role = aws_iam_role.flask_app_role.arn

}

################################################################################
# IAM role to get_viewer_count Lambda
################################################################################

resource "aws_iam_role" "flask_app_role" {
  name                = "flask_app_role"
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          }, {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "AWS" : [
            data.aws_caller_identity.current.account_id]
          },
          "Effect" : "Allow",
        }
      ]
  })
}
################################################################################
# CloudWatch logs
################################################################################

resource "aws_cloudwatch_log_group" "flask_app_logs" {
  name              = "/aws/lambda/${module.flask_app.lambda_function_name}"
  retention_in_days = 30
}

################################################################################
# API Gateway Integration 
################################################################################

resource "aws_apigatewayv2_api" "flask_app_api" {
  name          = "flask_api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "flask_integration" {
  api_id           = aws_apigatewayv2_api.flask_app_api.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "Lambda integration"
  integration_method   = "POST"
  integration_uri      = module.flask_app.lambda_function_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_apigatewayv2_route" "flask_route" {
  api_id    = aws_apigatewayv2_api.flask_app_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.flask_integration.id}"
}

resource "aws_apigatewayv2_stage" "flas_app_stage" {
  api_id      = aws_apigatewayv2_api.flask_app_api.id
  name        = "flask_app_stage"
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.flask_app_logs.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.flask_app.lambda_function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.flask_app_api.execution_arn}/*/*"
}