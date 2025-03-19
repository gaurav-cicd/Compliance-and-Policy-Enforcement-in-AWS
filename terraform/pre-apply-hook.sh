#!/bin/bash

# Exit on error
set -e

echo "Running pre-apply compliance checks..."

# Run Checkov on Terraform code
echo "Running Checkov on Terraform code..."
checkov -d .

# Run AWS Config rule validation
echo "Validating AWS Config rules..."
cd ../aws_config_rules
python3 validate_rules.py
cd ../terraform

# Run tag policy validation
echo "Validating tag policies..."
cd ../lambda_functions
python3 validate_tags.py
cd ../terraform

echo "Pre-apply checks completed successfully!" 