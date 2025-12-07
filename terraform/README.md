# Terraform Infrastructure

This Terraform configuration provisions AWS infrastructure for the Jewelry Shop Kubernetes cluster.

## Infrastructure Components

- **VPC**: Custom VPC with public subnets across 2 availability zones
- **EC2 Instances**: 3 instances (1 master + 2 workers) for Kubernetes cluster
- **Application Load Balancer**: Routes HTTP traffic (port 80) to Kubernetes NodePort
- **Security Groups**: Properly configured for Kubernetes cluster communication
- **Network**: Internet Gateway, Route Tables, and subnet associations

## Prerequisites

1. AWS CLI configured with credentials
2. Terraform >= 1.0
3. SSH key pair (see below)

## Setup

### 1. Download SSH Key (AWS Academy)

1. Go to AWS Academy Lab
2. Click "AWS Details"
3. Download `labsuser.pem`
4. Save it in a secure location
5. Set permissions: `chmod 400 labsuser.pem` (on Linux/Mac)

**Note**: `vockey` key pair already exists in AWS Academy, no need to create it.

### 2. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values.

### 3. Initialize Terraform

```bash
cd terraform
terraform init
```

### 4. Plan Infrastructure

```bash
terraform plan
```

### 5. Apply Infrastructure

```bash
terraform apply
```

Type `yes` when prompted.

## Outputs

After successful apply, you'll see:
- Load Balancer DNS name
- EC2 instance IPs (public and private)
- SSH commands to connect to instances

## Important Notes

- **NodePort**: ALB is configured to forward to port 30080 (Kubernetes NodePort)
- **Health Check**: ALB checks `/health` endpoint
- **Security**: Change `allowed_ssh_cidr` in tfvars to your IP for better security

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Next Steps

After infrastructure is provisioned:
1. Run Ansible playbooks to configure Kubernetes cluster
2. Deploy application using Helm charts
