#!/bin/bash
# Script to populate Ansible inventory from Terraform outputs

set -e

echo "Generating Ansible inventory from Terraform outputs..."

cd ../terraform

# Get Terraform outputs
MASTER_IP=$(terraform output -raw k8s_master_public_ip 2>/dev/null || echo "")
WORKER_IPS=$(terraform output -json k8s_workers_public_ips 2>/dev/null || echo "[]")

if [ -z "$MASTER_IP" ]; then
    echo "Error: Could not get master IP from Terraform"
    echo "Run 'terraform apply' first!"
    exit 1
fi

# Parse worker IPs
WORKER_1=$(echo $WORKER_IPS | jq -r '.[0]' 2>/dev/null || echo "")
WORKER_2=$(echo $WORKER_IPS | jq -r '.[1]' 2>/dev/null || echo "")

# Generate inventory file
cd ../ansible

cat > inventory.ini <<EOF
[k8s_master]
$MASTER_IP

[k8s_workers]
$WORKER_1
$WORKER_2

[k8s_cluster:children]
k8s_master
k8s_workers

[k8s_cluster:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=labsuser.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF

echo "✅ Inventory file generated successfully!"
echo ""
echo "Master: $MASTER_IP"
echo "Worker 1: $WORKER_1"
echo "Worker 2: $WORKER_2"
echo ""
echo "Next steps:"
echo "1. Copy labsuser.pem to ansible/ directory"
echo "2. Run: ansible-playbook -i inventory.ini setup-k8s-cluster.yml"
