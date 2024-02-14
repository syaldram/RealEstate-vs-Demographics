output "public_ip" {
  value       = aws_instance.terraform_EC2.public_ip
  description = "Public IP of the EC2 instance"
}

output "ssh_command" {
  value       = "\nssh -i ${var.key_name}.pem ubuntu@${aws_instance.terraform_EC2.public_ip}\n"
  description = "SSH command to connect to the EC2 instance"
}