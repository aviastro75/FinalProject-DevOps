output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "k8s_master_public_ip" {
  description = "Public IP of Kubernetes master node"
  value       = aws_instance.k8s_master.public_ip
}

output "k8s_master_private_ip" {
  description = "Private IP of Kubernetes master node"
  value       = aws_instance.k8s_master.private_ip
}

output "k8s_workers_public_ips" {
  description = "Public IPs of Kubernetes worker nodes"
  value       = aws_instance.k8s_workers[*].public_ip
}

output "k8s_workers_private_ips" {
  description = "Private IPs of Kubernetes worker nodes"
  value       = aws_instance.k8s_workers[*].private_ip
}

output "load_balancer_dns" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ssh_commands" {
  description = "SSH commands to connect to instances"
  value = {
    master   = "ssh -i labsuser.pem ubuntu@${aws_instance.k8s_master.public_ip}"
    worker_1 = "ssh -i labsuser.pem ubuntu@${aws_instance.k8s_workers[0].public_ip}"
    worker_2 = "ssh -i labsuser.pem ubuntu@${aws_instance.k8s_workers[1].public_ip}"
  }
}
