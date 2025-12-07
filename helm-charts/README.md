# Helm Charts for Jewelry Shop

This directory contains Helm charts for deploying the Jewelry Shop application to Kubernetes.

## Prerequisites

1. Kubernetes cluster running (master + workers)
2. Helm 3.x installed
3. kubectl configured to access the cluster
4. NFS server running on master node
5. Docker image pushed to Docker Hub

## Chart Structure

```
jewelry-shop/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── values-production.yaml  # Production overrides
├── templates/
│   ├── deployment.yaml     # Application deployment
│   ├── service.yaml        # NodePort service (port 30080)
│   ├── pv.yaml            # NFS PersistentVolume
│   ├── pvc.yaml           # PersistentVolumeClaim
│   ├── _helpers.tpl       # Template helpers
│   └── NOTES.txt          # Post-install notes
└── .helmignore
```

## Quick Start

### 1. Install Helm (if not installed)

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

### 2. Get NFS Server IP

SSH to the master node and get its private IP:

```bash
# On your local machine
cd terraform
terraform output k8s_master_public_ip

# SSH to master
ssh -i labsuser.pem ubuntu@<master-ip>

# Get private IP
hostname -I | awk '{print $1}'
```

### 3. Update Helm Values

Edit `helm-charts/jewelry-shop/values.yaml`:

```yaml
image:
  repository: your-dockerhub-username/jewelry-shop  # Change this
  tag: "latest"

persistence:
  nfsServer: "10.0.1.10"  # Change to your master private IP
```

### 4. Deploy with Helm

```bash
# From master node or local machine with kubectl access
cd helm-charts

# Validate chart
helm lint jewelry-shop

# Dry run (see what will be created)
helm install jewelry-shop jewelry-shop --dry-run --debug

# Install
helm install jewelry-shop jewelry-shop

# Or install with custom values
helm install jewelry-shop jewelry-shop \
  --set image.repository=your-dockerhub-username/jewelry-shop \
  --set persistence.nfsServer=10.0.1.10
```

### 5. Verify Deployment

```bash
# Check release status
helm status jewelry-shop

# Check pods
kubectl get pods -l app.kubernetes.io/name=jewelry-shop

# Check service
kubectl get svc jewelry-shop

# Check PV/PVC
kubectl get pv,pvc

# View logs
kubectl logs -l app.kubernetes.io/name=jewelry-shop --tail=50 -f
```

## Deployment Options

### Development Deployment

Uses default values (2 replicas, basic resources):

```bash
helm install jewelry-shop jewelry-shop \
  --set persistence.nfsServer=<master-private-ip>
```

### Production Deployment

Uses production values (3 replicas, autoscaling, more resources):

```bash
helm install jewelry-shop jewelry-shop \
  -f jewelry-shop/values-production.yaml \
  --set persistence.nfsServer=<master-private-ip>
```

### Custom Namespace

```bash
kubectl create namespace jewelry-prod
helm install jewelry-shop jewelry-shop \
  --namespace jewelry-prod \
  --set persistence.nfsServer=<master-private-ip>
```

## Upgrading

After making changes to the chart or updating Docker image:

```bash
# Upgrade existing release
helm upgrade jewelry-shop jewelry-shop

# Upgrade with new image tag
helm upgrade jewelry-shop jewelry-shop \
  --set image.tag=v2.0

# Force restart pods
helm upgrade jewelry-shop jewelry-shop --force
```

## Uninstalling

```bash
# Uninstall release
helm uninstall jewelry-shop

# Delete PV/PVC manually if needed
kubectl delete pv jewelry-shop-pv
kubectl delete pvc jewelry-shop-pvc
```

## Configuration

### Important Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Docker image repository | `your-dockerhub-username/jewelry-shop` |
| `image.tag` | Image tag | `latest` |
| `service.type` | Service type | `NodePort` |
| `service.nodePort` | NodePort number | `30080` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.nfsServer` | NFS server IP (master private IP) | `""` (required) |
| `persistence.nfsPath` | NFS export path | `/srv/nfs/jewelry-data` |
| `persistence.size` | PV size | `1Gi` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |

### Override Values

Create a custom values file:

```yaml
# my-values.yaml
replicaCount: 3

image:
  repository: myuser/jewelry-shop
  tag: "v1.2.3"

persistence:
  nfsServer: "10.0.1.10"
  size: 2Gi

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
```

Deploy with custom values:

```bash
helm install jewelry-shop jewelry-shop -f my-values.yaml
```

## Accessing the Application

### Via NodePort (Default)

The application is exposed on NodePort 30080:

```bash
# Get any worker node IP
kubectl get nodes -o wide

# Access application
curl http://<any-node-ip>:30080/
```

### Via Load Balancer

The AWS ALB (configured by Terraform) forwards port 80 to NodePort 30080:

```bash
# Get ALB DNS from Terraform
cd terraform
terraform output alb_dns_name

# Access via ALB
curl http://<alb-dns-name>/
```

## Health Checks

The deployment includes health checks:

- **Liveness Probe**: `/health` endpoint, checks if app is running
- **Readiness Probe**: `/health` endpoint, checks if app is ready to serve traffic

```bash
# Test health endpoint
kubectl port-forward svc/jewelry-shop 8080:80
curl http://localhost:8080/health
```

## Persistent Storage

The application uses NFS for persistent storage:

- **PersistentVolume**: NFS volume pointing to master node
- **PersistentVolumeClaim**: Claimed by all pods
- **Mount Path**: `/var/www/flask_app/data`

All pods share the same JSON data file via NFS.

```bash
# Verify NFS mount in pod
kubectl exec -it <pod-name> -- df -h | grep nfs
kubectl exec -it <pod-name> -- ls -la /var/www/flask_app/data
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=jewelry-shop

# View pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### NFS mount issues

```bash
# Verify NFS is running on master
ssh -i labsuser.pem ubuntu@<master-ip>
showmount -e localhost

# Check PV status
kubectl describe pv jewelry-shop-pv

# Check PVC status
kubectl describe pvc jewelry-shop-pvc
```

### Image pull errors

```bash
# Check image repository and tag
kubectl describe pod <pod-name> | grep Image

# Verify image exists on Docker Hub
docker pull your-dockerhub-username/jewelry-shop:latest
```

### Service not accessible

```bash
# Check service endpoints
kubectl get endpoints jewelry-shop

# Verify NodePort
kubectl get svc jewelry-shop

# Test from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://jewelry-shop/health
```

## Helm Commands Cheat Sheet

```bash
# List releases
helm list

# Get release status
helm status jewelry-shop

# Get release values
helm get values jewelry-shop

# Get release manifests
helm get manifest jewelry-shop

# History of releases
helm history jewelry-shop

# Rollback to previous version
helm rollback jewelry-shop

# Rollback to specific revision
helm rollback jewelry-shop 1

# Test release (run test pods)
helm test jewelry-shop

# Package chart
helm package jewelry-shop

# Validate chart
helm lint jewelry-shop
```

## Next Steps

After Helm deployment:
1. Access application via ALB DNS name
2. Test CRUD operations (add/update/delete jewelry items)
3. Verify data persistence across pod restarts
4. Monitor application logs and metrics
5. Set up CI/CD pipeline for automated deployments
