# DevOps Final Project - Jewelry Shop Inventory Management System

***Students Names: Basil Mousa and Avi Astrogano***

**Project Title:** Jewelry Shop Inventory Management System – Full DevOps Pipeline  
**Repository:** https://github.com/BasilMousa/devops-final-project

This project implements all required components of the DevOps Final Project (application, Terraform, Ansible, Kubernetes, Helm, and CI/CD with GitHub Actions).

---

## 1. Project Overview

This project is a Flask web application for managing jewelry shop inventory with features including:

- View all jewelry items
- Add new items
- Edit existing items
- Delete items
- Calculate total profit
- Track sold items

For the final DevOps project, the application was:

- Switched from in-memory storage to **file-based persistence** (JSON file).
- **Containerized with Docker** and pushed to Docker Hub: `your_docker_user/jewelry-shop:latest`.
- **Deployed to a Kubernetes cluster** (1 master + 2 workers) on AWS.
- **Infrastructure provisioned with Terraform** (VPC, EC2 instances, Application Load Balancer).
- **Nodes configured with Ansible** (Kubernetes 1.28 + Flannel CNI + NFS server).
- **Application deployed using Helm chart** with persistent storage.
- **End-to-end automation with GitHub Actions CI/CD pipeline**.

On first start, the app creates **8 dummy jewelry items**, so the UI is ready immediately with sample data.

---

## 2. How to Get the Code

```bash
git clone https://github.com/BasilMousa/devops-final-project

```

**Main components:**

- **Application** – `app.py`, `functions.py`, `templates/`, `static/`
- **Docker** – `Dockerfile`, `.dockerignore`, `requirements.txt`
- **Terraform** – `terraform/` (7 files: main, variables, ec2, vpc, alb, security_groups, outputs)
- **Ansible** – `ansible/setup-k8s-cluster.yml`, `ansible.cfg`
- **Helm chart** – `helm-charts/jewelry-shop/`
- **CI/CD workflows** – `.github/workflows/` (deploy.yml, app-update.yml, destroy.yml, helm-only.yml, helm-cleanup.yml)

---

## 3. Required Tools

### For running the CI/CD pipeline (GitHub Actions + AWS):

**Accounts / Services:**
- AWS account 
- Existing EC2 key pair named **`vockey`** in us-east-1 region
- Docker Hub account
- GitHub repository with this project

**Tools** (used inside GitHub runner; no local installation needed):
- Python 3.11
- Docker
- Terraform 1.6.0
- Ansible 2.x
- kubectl (latest stable)
- Helm 3.14.0

### For manual local deployment:

Install the following on your machine:
- Terraform ≥ 1.6.0
- Ansible ≥ 2.9
- AWS CLI
- kubectl
- helm 3.x
- SSH client

---

## 4. GitHub Secrets and AWS Credentials

All sensitive data is passed through **GitHub Actions Secrets**.

In your repository, go to: **Settings → Secrets and variables → Actions** and create:

| Secret Name | Description | Example Value |
|------------             |-------------                    |---------------                                                             |
| `AWS_ACCESS_KEY_ID`     | AWS access key                  | `AKIAIOSFODNN7EXAMPLE`                                                     |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key                  | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`                                 |
| `AWS_SESSION_TOKEN`     | AWS session token (AWS ) | `FwoGZXIvYXdzE...` (long string)                                           |
| `DOCKER_USERNAME`       | Docker Hub username             | `your_docker_user`                                                  |
| `DOCKER_PASSWORD`       | Docker Hub password/token       | Your Docker Hub access token                                               |
| `SSH_PRIVATE_KEY`       | Private key for vockey          | Full content of `labsuser.pem` including `-----BEGIN` and `-----END` lines |

**Important Notes:**
- For AWS , copy credentials from **AWS Details** (refresh every ~4 hours)
- `SSH_PRIVATE_KEY` should be the downloaded `labsuser.pem` from AWS 
- Docker Hub token is recommended over password (Settings → Security → Access Tokens)

---

## 5. How to Trigger the CI/CD Pipeline

**Workflow file:** `.github/workflows/deploy.yml`  
**Workflow name:** CI/CD Pipeline - Deploy Jewelry Shop

### Manual run steps:

1. Make sure all secrets from section 4 are configured.
2. Go to the **Actions** tab in GitHub.
3. Select **CI/CD Pipeline - Deploy Jewelry Shop**.
4. Click **Run workflow** (branch: main).
5. Select deployment options:
   - ✅ Deploy infrastructure (Terraform + Ansible) – Check for full deployment
   - ✅ Deploy application (Docker + Helm) – Check to deploy the app
6. Click **Run workflow** button.
7. Wait until all jobs finish (~25-35 minutes for full deployment).

### Automatic run:

- comment and push to main branch to trigger the workflow

---
## 6. Pipeline Stages (CI/CD Workflow)

The workflow consists of **6 jobs** running on `ubuntu-latest`:

### **Job 1: Run Tests**
- Checkout repository
- Set up Python 3.11
- Install dependencies
- Run pytest (if tests exist)

### **Job 2: Build & Push Docker Image**
- Set up Docker Buildx
- Login to Docker Hub
- Extract metadata (tags, labels)
- Build and push Docker image
- Cache layers for faster builds

### **Job 3: Terraform Infrastructure**
- Configure AWS credentials
- Setup Terraform 1.6.0
- Terraform init, validate, plan
- **Terraform apply** (creates VPC, 3 EC2 instances, ALB, security groups)
- Export outputs (master IP, worker IPs, ALB DNS)
- Save terraform state as artifact

### **Job 4: Ansible K8s Setup**
- Install Ansible
- Setup SSH key (`labsuser.pem`)
- Generate Ansible inventory (master + 2 workers)
- Wait 60s for EC2 instances to be ready
- Test connectivity (ping all nodes)
- **Run Kubernetes setup playbook** (~10-15 minutes):
  - Install containerd runtime
  - Install Kubernetes 1.28
  - Initialize master node
  - Join worker nodes
  - Setup Flannel CNI
  - Configure NFS server on master
  - Install Helm on master
- Save kubeconfig as artifact

### **Job 5: Helm Deployment**
- Setup SSH key
- Determine master IP (from Terraform or secrets)
- Get NFS server IP (master private IP)
- Verify cluster connectivity
- Copy Helm chart to master node
- **Deploy with Helm** (via SSH on master):
  - Set image repository
  - Set NFS server IP
  - Wait for deployment (timeout: 10m)
- Verify deployment (pods, service, PV/PVC)
- Display service endpoint and ALB URL

### **Job 6: Health Check**
- Wait 30s for stabilization
- Test health endpoint via ALB
- Retry up to 10 times with 10s intervals
- Report success or failure

---

## 7. How to Find the Load Balancer URL

After a successful pipeline run:

1. Open the workflow run in the **Actions** tab.
2. Scroll to **Job 5: Helm Deployment** → Step: **Get service endpoint**.
3. In the logs you will see:
   ```
   Access via ALB: http://jewelry-shop-alb-XXXXXXXXX.us-east-1.elb.amazonaws.com
   ```
4. Open this URL in a browser.

**Traffic flow:**
- Internet → ALB (port 80) → EC2 NodePort (30080) → Kubernetes Service → Pods (port 80)

---

## 8. Manual Deployment (Alternative to CI/CD)

If you want to deploy manually from your local machine:

### Prerequisites:
```bash
# Download SSH key from AWS 
cp ~/Downloads/labsuser.pem ansible/
chmod 400 ansible/labsuser.pem
```

### Step 1: Deploy Infrastructure with Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve

# Save outputs
terraform output k8s_master_public_ip
terraform output k8s_workers_public_ips
terraform output load_balancer_dns
```

### Step 2: Configure Kubernetes with Ansible
```bash
cd ../ansible

# Generate inventory
bash generate-inventory.sh

# Verify connectivity
ansible all -i inventory.ini -m ping

# Run playbook (10-15 minutes)
ansible-playbook -i inventory.ini setup-k8s-cluster.yml
```

### Step 3: Deploy Application with Helm
```bash
# Get master IP from Terraform output
MASTER_IP=$(cd ../terraform && terraform output -raw k8s_master_public_ip)

# Get NFS server IP (master private IP)
NFS_IP=$(ssh -i labsuser.pem ubuntu@$MASTER_IP "hostname -I | awk '{print \$1}'")

# Copy Helm chart to master
scp -i labsuser.pem -r ../helm-charts/jewelry-shop ubuntu@$MASTER_IP:~/

# Deploy with Helm
ssh -i labsuser.pem ubuntu@$MASTER_IP \
  "helm upgrade --install jewelry-shop ~/jewelry-shop \
    --set image.repository=your_docker_user/jewelry-shop \
    --set image.tag=latest \
    --set persistence.nfsServer=$NFS_IP"
```

### Step 4: Verify Deployment
```bash
# SSH to master
ssh -i labsuser.pem ubuntu@$MASTER_IP

# Check nodes
kubectl get nodes

# Check pods
kubectl get pods

# Check service
kubectl get svc jewelry-shop

# Check NFS
showmount -e localhost
```

---

## 9. Architecture Overview

### Infrastructure (Terraform):
- **VPC:** 10.0.0.0/16
- **Subnets:** 2 public subnets (10.0.1.0/24, 10.0.2.0/24) in different AZs
- **EC2 Instances:** 
  - 1 master node (t2.small, 2GB RAM, 1 vCPU)
  - 2 worker nodes (t2.small, 2GB RAM, 1 vCPU)
- **ALB:** Application Load Balancer forwarding to NodePort 30080
- **Security Groups:** Configured for K8s, SSH, HTTP, and NodePort traffic

### Kubernetes Cluster (Ansible):
- **Version:** 1.28
- **Runtime:** containerd with SystemdCgroup
- **CNI:** Flannel (pod network: 10.244.0.0/16)
- **Storage:** NFS server on master node (`/srv/nfs/jewelry-data`)
- **Tools:** kubectl, helm 3.14.0

### Application (Helm):
- **Replicas:** 2 pods with anti-affinity (distributed across workers)
- **Service:** NodePort on 30080
- **Persistence:** NFS PersistentVolume (1Gi, ReadWriteMany)
- **Health Checks:** Liveness and readiness probes on `/health`
- **Resources:** 250m CPU / 256Mi RAM (request), 500m CPU / 512Mi RAM (limit)

### Data Persistence:
- JSON file stored at `/var/www/flask_app/data/inventory.json`
- Mounted from NFS share on all pods
- Survives pod restarts and deletions
- Shared across all replicas

---


## 11. Troubleshooting

### Common Issues:

#### **Pipeline fails on Terraform**
- Check AWS secrets are correctly configured
- Verify AWS credentials are not expired (AWS : refresh every 4 hours)
- Check IAM permissions for EC2, VPC, ELB operations
- Ensure `vockey` key pair exists in us-east-1

#### **Ansible cannot connect to hosts**
- Verify `SSH_PRIVATE_KEY` secret contains the correct `labsuser.pem` content
- Check security group allows SSH (port 22) from 0.0.0.0/0
- Wait longer for EC2 instances to initialize (increase sleep time)

#### **Pods in CrashLoopBackOff**
- Check pod logs: `kubectl logs <pod-name>`
- Common causes:
  - Incorrect image repository in values.yaml
  - Missing NFS mount
  - Permission issues (should run as root, not www-data)
  
#### **ALB returns 502 Bad Gateway**
- Verify pods are running: `kubectl get pods`
- Check NodePort service: `kubectl get svc jewelry-shop`
- Test locally on master: `curl http://localhost:30080/health`
- Verify security groups allow ALB → NodePort (30000-32767)

#### **Docker push fails**
- `DOCKER_USERNAME` and `DOCKER_PASSWORD` must match Docker Hub credentials
- Use access token instead of password (more secure)

#### **Health check fails**
- ALB needs time to mark targets as healthy (2-3 minutes)
- Check target group in AWS Console
- Verify `/health` endpoint works: `curl http://<alb-dns>/health`

### Logs:

- **CI/CD:** GitHub → Actions → run details → expand each step
- **Terraform:** Steps "Terraform Init / Plan / Apply"
- **Ansible:** Step "Run Kubernetes setup playbook" (verbose output)
- **Helm:** Step "Deploy with Helm" (--debug flag enabled)
- **Application:** `kubectl logs -l app.kubernetes.io/name=jewelry-shop`

---

## 12. Project Structure

```
devops-final-project-main/
├── .github/workflows/          # CI/CD pipelines
│   ├── deploy.yml             # Main deployment workflow
│   ├── app-update.yml         # Quick app updates
│   ├── destroy.yml            # Infrastructure cleanup
│   ├── helm-only.yml          # Helm-only deployment
│   └── helm-cleanup.yml       # Helm cleanup utility
├── ansible/                    # Ansible configuration
│   ├── setup-k8s-cluster.yml  # Main playbook (7 plays)
│   ├── ansible.cfg            # Ansible settings
│   ├── inventory.ini          # Generated inventory
│   ├── generate-inventory.sh  # Inventory generator
│   └── labsuser.pem          # SSH key (gitignored, you must add)
├── helm-charts/jewelry-shop/   # Helm chart
│   ├── Chart.yaml             # Chart metadata
│   ├── values.yaml            # Default values
│   ├── templates/             # Kubernetes manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── pv.yaml           # NFS PersistentVolume
│   │   ├── pvc.yaml          # PersistentVolumeClaim
│   │   ├── _helpers.tpl      # Template helpers
│   │   └── NOTES.txt         # Post-install notes
│   └── .helmignore
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                # Provider configuration
│   ├── variables.tf           # Variable definitions
│   ├── terraform.tfvars       # Variable values
│   ├── ec2.tf                 # EC2 instances
│   ├── vpc.tf                 # VPC and networking
│   ├── alb.tf                 # Application Load Balancer
│   ├── security_groups.tf     # Security rules
│   └── outputs.tf             # Output values
├── templates/                  # Flask HTML templates
│   ├── menu.html              # Main menu
│   ├── show.html              # View inventory
│   ├── add.html               # Add items
│   ├── update.html            # Edit items
│   ├── sold.html              # Sold items
│   └── profit.html            # Profit calculation
├── static/                     # Static assets (if any)
├── app.py                      # Flask application
├── functions.py                # Business logic
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── .dockerignore              # Docker build exclusions
├── .gitignore                 # Git exclusions
└── README.md                  
```

---

## 13. Application Features

### Main Menu:
- **Show Inventory** – View all jewelry items with details
- **Add Item** – Create new jewelry entry
- **Update Item** – Edit existing item by ID
- **Show Sold Items** – View items marked as sold
- **Calculate Profit** – Total profit from all items

### Data Fields:
- ID (auto-generated)
- Name
- Type (ring, necklace, bracelet, earrings)
- Purchase Price
- Sale Price
- Sold Status (Yes/No)
- Date Added

### Storage:
- All data stored in `/var/www/flask_app/data/inventory.json`
- Persistent across pod restarts via NFS
- Shared across all pod replicas
- Initial 8 dummy items created on first run

---

## 14. Technologies Used

| Category               | Technology          |Version |
|----------              |-----------          |--------|
| **Application**        | Python Flask        | 2.3.x  |
| **Containerization**   | Docker              | latest |
| **Container Registry** | Docker Hub          | -      |
| **Infrastructure**     | Terraform           | 1.6.0  |
| **Cloud Provider**     | AWS (EC2, VPC, ALB) | -      |
| **Configuration Mgmt** | Ansible             | 2.x    |
| **Orchestration**      | Kubernetes          | 1.28   |
| **Container Runtime**  | containerd          | latest |
| **CNI Plugin**         | Flannel             | latest |
| **Package Manager**    | Helm                | 3.14.0 |
| **Shared Storage**     | NFS                 | kernel |
| **CI/CD**              | GitHub Actions      | -      |
| **Web Server**         | Apache + mod_wsgi   | 2.4    |

---

## 15. Security Considerations

- **SSH Keys:** Private key stored as GitHub secret, never committed to repo
- **AWS Credentials:** Temporary session tokens (AWS ), rotated frequently
- **Docker Registry:** Access token used instead of password
- **Network Security:** Security groups limit access to required ports only
- **Container Security:** Application runs as root (required for Apache port 80)
- **Data Persistence:** NFS exports restricted to VPC CIDR (10.0.0.0/16)

---

## 16. Future Improvements

- Add HTTPS support with SSL certificates
- Implement database backend (PostgreSQL/MySQL)
- Add user authentication and authorization
- Configure Horizontal Pod Autoscaler (HPA)
- Set up monitoring with Prometheus and Grafana
- Implement logging aggregation with ELK stack
- Add backup and disaster recovery for NFS data
- Use remote backend for Terraform state (S3 + DynamoDB)
- Implement blue-green or canary deployments
- Add integration and end-to-end tests

---

**Last Updated:** 08 December 2025
