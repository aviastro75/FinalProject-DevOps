# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-alb"
  }
}

# Target Group for Kubernetes NodePort
resource "aws_lb_target_group" "k8s_app" {
  name     = "${var.project_name}-k8s-tg"
  port     = 30080  # Kubernetes NodePort (will be configured in Helm)
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-k8s-tg"
  }
}

# Register EC2 instances to Target Group
resource "aws_lb_target_group_attachment" "master" {
  target_group_arn = aws_lb_target_group.k8s_app.arn
  target_id        = aws_instance.k8s_master.id
  port             = 30080
}

resource "aws_lb_target_group_attachment" "workers" {
  count            = length(aws_instance.k8s_workers)
  target_group_arn = aws_lb_target_group.k8s_app.arn
  target_id        = aws_instance.k8s_workers[count.index].id
  port             = 30080
}

# Listener for HTTP traffic
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.k8s_app.arn
  }
}
