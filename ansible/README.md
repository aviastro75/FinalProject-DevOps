# Ansible for Kubernetes Cluster Setup

This directory contains Ansible playbooks to configure a Kubernetes cluster on AWS EC2 instances.

## What It Does

1. **Prepares all nodes**: Installs containerd, disables swap, configures kernel parameters
2. **Installs Kubernetes**: Installs kubelet, kubeadm, kubectl on all nodes
3. **Initializes master**: Sets up Kubernetes control plane with Flannel CNI
4. **Joins workers**: Connects worker nodes to the cluster
5. **Sets up NFS**: Configures NFS server on master for persistent storage
6. **Verifies cluster**: Checks all nodes are ready

## Prerequisites

1. Terraform infrastructure deployed (3 EC2 instances running)
2. `labsuser.pem` SSH key downloaded from AWS Academy
3. Ansible installed on your local machine

### Install Ansible

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ansible
```

**MacOS:**
```bash
brew install ansible
```

**Windows (WSL):**
```bash
sudo apt update
sudo apt install ansible
```

## Setup Steps

### 1. Copy SSH Key

```bash
cp ~/Downloads/labsuser.pem ansible/
chmod 400 ansible/labsuser.pem
```

### 2. Generate Inventory from Terraform

```bash
cd ansible
bash generate-inventory.sh
```

This reads Terraform outputs and creates `inventory.ini` with your EC2 IPs.

### 3. Test Connectivity

```bash
ansible all -i inventory.ini -m ping
```

Should return "pong" from all nodes.

### 4. Run Kubernetes Setup Playbook

```bash
ansible-playbook -i inventory.ini setup-k8s-cluster.yml
```

This takes ~10-15 minutes to complete.

## Manual Inventory Setup (Alternative)

If `generate-inventory.sh` doesn't work, manually edit `inventory.ini`:

```ini
[k8s_master]
54.123.45.67

[k8s_workers]
54.123.45.68
54.123.45.69

[k8s_cluster:children]
k8s_master
k8s_workers

[k8s_cluster:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=labsuser.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

Get IPs from:
```bash
cd ../terraform
terraform output
```

## Verification

### SSH to master node:

```bash
ssh -i labsuser.pem ubuntu@<master-ip>
```

### Check cluster status:

```bash
kubectl get nodes
kubectl get pods -A
```

All nodes should show "Ready" status.

### Check NFS:

```bash
showmount -e localhost
```

Should show: `/srv/nfs/jewelry-data *`

## Troubleshooting

### Ansible connection fails:
- Check `labsuser.pem` permissions: `chmod 400 labsuser.pem`
- Verify Security Group allows SSH (port 22)
- Check EC2 instances are running

### Kubernetes nodes not ready:
- SSH to node and check: `journalctl -u kubelet -f`
- Verify containerd is running: `systemctl status containerd`

### NFS not working:
- Check NFS server: `systemctl status nfs-kernel-server`
- Verify exports: `cat /etc/exports`

## What's Configured

- **Container Runtime**: containerd
- **Kubernetes Version**: 1.28.x
- **CNI Plugin**: Flannel (pod network)
- **NFS Server**: Master node at `/srv/nfs/jewelry-data`
- **NFS Access**: All nodes can mount NFS share

## Next Steps

After Kubernetes cluster is ready:
1. Deploy application using Helm charts
2. Configure LoadBalancer to forward to NodePort
3. Test application accessibility
