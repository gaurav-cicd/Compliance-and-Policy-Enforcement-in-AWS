#!/bin/bash

# Exit on error
set -e

echo "Starting deployment of AWS Compliance and Policy Enforcement components..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v pip >/dev/null 2>&1 || { echo "pip is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Terraform is required but not installed. Aborting." >&2; exit 1; }
command -v checkov >/dev/null 2>&1 || { echo "Checkov is required but not installed. Installing..."; pip install checkov; }

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create Lambda deployment package
echo "Creating Lambda deployment package..."
cd lambda_functions
zip -r tag_enforcement.zip tag_enforcement.py
cd ..

# Make pre-apply hook executable
echo "Setting up pre-apply hook..."
cd terraform
chmod +x pre-apply-hook.sh
cd ..

# Run Checkov on Terraform code
echo "Running Checkov on Terraform code..."
cd terraform
checkov -d .
cd ..

# Initialize and apply Terraform
echo "Initializing Terraform..."
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ..

echo "Deployment completed successfully!"
echo "Please check the AWS Console to verify the resources have been created correctly." 