variable "vpc" {
  type      = string
  default   = "vpc-04eb4c31ecd843898"
  sensitive = false
}

variable "EC2_instance_type" {
  description = "The type of instance to start"
}

variable "EC2_SecurityGroup_Name" {
  type        = string
  description = "Name of the security group to be part of EC2 instance."
}

variable "key_name" {
  type        = string
  description = "Name of an EC2 Key to enable SSH access to the instance"
}

variable "EC2_Subnet" {
  type        = string
  description = "Provide a subnet ID to launch an ec2 instance."
  sensitive   = false
}

variable "iam_role_name" {
  type        = string
  description = "Provide a name for the EC2 IAM role."
}

variable "ami_id" {
  type        = string
  description = "EC2 image to use with flask app"
}

variable "certificate_arn" {
  type        = string
  description = "ARN of your ACM certificate"
}