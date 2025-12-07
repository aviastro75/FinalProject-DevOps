# EC2 Key Pair - using vockey from AWS Academy
# No need to create key pair as vockey already exists in lab environment

# EC2 Instance - Master Node
resource "aws_instance" "k8s_master" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.k8s_nodes.id]

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              hostnamectl set-hostname k8s-master
              echo "127.0.0.1 k8s-master" >> /etc/hosts
              EOF

  tags = {
    Name = "${var.project_name}-k8s-master"
    Role = "master"
  }
}

# EC2 Instances - Worker Nodes
resource "aws_instance" "k8s_workers" {
  count                  = 2
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = aws_subnet.public[count.index % length(aws_subnet.public)].id
  vpc_security_group_ids = [aws_security_group.k8s_nodes.id]

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              hostnamectl set-hostname k8s-worker-${count.index + 1}
              echo "127.0.0.1 k8s-worker-${count.index + 1}" >> /etc/hosts
              EOF

  tags = {
    Name = "${var.project_name}-k8s-worker-${count.index + 1}"
    Role = "worker"
  }
}
