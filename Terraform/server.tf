data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

################################################################################
# Generate SSH key for port 22
################################################################################

resource "tls_private_key" "generated" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = var.key_name
  public_key = tls_private_key.generated.public_key_openssh

  provisioner "local-exec" {
    command = <<-EOT
    echo '${tls_private_key.generated.private_key_pem}' > ./'${var.key_name}'.pem 
    chmod 400 ./'${var.key_name}'.pem
    EOT
  }
}

################################################################################
# Create a Security Group
################################################################################

resource "aws_security_group" "EC2SecurityGroup" {
  name        = var.EC2_SecurityGroup_Name
  description = "Flask App security group"
  vpc_id      = var.vpc

  ingress {
    description = "Allows access on port 22"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allows access on port 80"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allows access on port 443"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allows all traffic out"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] #tfsec:ignore:aws-vpc-no-public-egress-sgr
  }

  tags = {
    Name = "real-estate-demographics-sg"
  }

}

################################################################################
# Create a EC2 instance
################################################################################

resource "aws_instance" "terraform_EC2" {
  ami                         = var.ami_id
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  instance_type               = var.EC2_instance_type
  security_groups             = [aws_security_group.EC2SecurityGroup.id]
  subnet_id                   = var.EC2_Subnet
  key_name                    = aws_key_pair.generated_key.key_name
  associate_public_ip_address = true

  user_data = <<-EOF1
  #!/bin/bash
  # Install necessary packages
  sudo apt update
  sudo apt install -y git nginx

  EOF1

  tags = {
    Name = "real-estate-demographics-ec2"
  }

  lifecycle {
    ignore_changes        = [security_groups]
    create_before_destroy = true
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
}


################################################################################
# EC2 instance role
################################################################################

resource "aws_iam_role" "terraform_ec2_role" {
  name = var.iam_role_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "flask_policy" {
  name = "flask-app"
  role = aws_iam_role.terraform_ec2_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Effect = "Allow",
        Resource = ["arn:aws:logs:*:*:*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.iam_role_name}-profile"
  role = aws_iam_role.terraform_ec2_role.name
}

################################################################################
# Cloudfront Distribution
################################################################################

locals {
  ec2_origin_id = "SyEC2Origin"
}

resource "aws_cloudfront_distribution" "ec2_distribution" {
  origin {
    domain_name = aws_instance.terraform_EC2.public_dns
    origin_id   = local.ec2_origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront Distribution for EC2 instance"
  default_root_object = "index.html"

  aliases = ["data.saadyaldram.com"]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.ec2_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
  }

  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Environment = "production"
    Name        = "flask-app"
  }
}
