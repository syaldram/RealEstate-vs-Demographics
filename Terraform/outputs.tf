output "private_ip" {
  value       = aws_instance.terraform_EC2.private_ip
  description = "Private IP of the EC2 instance"
}

output "ssh_command" {
  value       = "\nssh -i ${var.key_name}.pem ec2-user@${aws_instance.terraform_EC2.private_ip}\n"
  description = "SSH command to connect to the EC2 instance"
}