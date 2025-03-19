<<<<<<< HEAD
# Compliance-and-Policy-Enforcement-in-AWS
=======
# AWS Compliance and Policy Enforcement

This project implements automated compliance and policy enforcement mechanisms for AWS environments using AWS Config rules, Lambda functions, and Terraform compliance checks. The solution ensures that all infrastructure changes meet compliance requirements before deployment.

## Project Structure

```
.
├── aws_config_rules/          # AWS Config custom rules
│   ├── ec2_encryption_rule.py # Custom rule for EC2 encryption
│   └── validate_rules.py      # Rule validation script
├── lambda_functions/         # Lambda functions for tagging enforcement
│   ├── tag_enforcement.py    # Tag enforcement Lambda
│   └── validate_tags.py      # Tag policy validation
├── terraform/               # Terraform configurations
│   ├── main.tf             # Main Terraform configuration
│   ├── variables.tf        # Terraform variables
│   ├── pre-apply-hook.sh   # Pre-apply compliance checks
│   └── .checkov.yaml       # Checkov configuration
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── deploy.sh               # Deployment script
```

## Components

### 1. AWS Config Rule Automation
- Custom AWS Config rules implemented in Python
- Enforces compliance across AWS accounts
- Monitors resource configurations and states
- Validates rules before deployment

### 2. Tagging Policy Enforcement
- Lambda function to check AWS resources for missing tags
- Sends alerts for non-compliant resources
- Supports custom tag policies
- Validates tag policies before deployment

### 3. Terraform Compliance Checks
- Integration with Checkov for security scanning
- Pre-deployment compliance validation
- Automated misconfiguration detection
- Runs automatically during every Terraform apply

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate credentials
- Terraform installed
- Checkov installed (`pip install checkov`)

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aws-compliance-enforcement
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials:
   ```bash
   aws configure
   ```

4. Deploy the components:
   ```bash
   ./deploy.sh
   ```

## Automated Compliance Checks

The project implements automated compliance checks that run during every Terraform apply:

1. **Pre-apply Hook**:
   - Runs Checkov on Terraform code
   - Validates AWS Config rules
   - Validates tag policies
   - Blocks deployment if any checks fail

2. **Validation Process**:
   - AWS Config Rules: Checks for rule existence and configuration
   - Tag Policies: Validates required components and tag structure
   - Infrastructure: Scans for security misconfigurations

3. **Deployment Flow**:
   ```bash
   terraform apply
   ↓
   Pre-apply hook execution
   ↓
   Compliance checks
   ↓
   If checks pass → Apply changes
   If checks fail → Block deployment
   ```

## Usage

### AWS Config Rules
```bash
cd aws_config_rules
python3 validate_rules.py
```

### Tagging Policy Enforcement
```bash
cd lambda_functions
python3 validate_tags.py
```

### Terraform Compliance Checks
```bash
cd terraform
checkov -d .
```

### Manual Deployment
```bash
./deploy.sh
```

## Customization

### AWS Config Rules
1. Modify `aws_config_rules/ec2_encryption_rule.py` to add custom rules
2. Update validation in `validate_rules.py`

### Tag Policies
1. Edit `REQUIRED_TAGS` in `lambda_functions/tag_enforcement.py`
2. Update validation in `validate_tags.py`

### Checkov Rules
1. Modify `terraform/.checkov.yaml` to customize security checks
2. Add custom checks in the Checkov configuration

## Monitoring and Alerts

- Tag compliance alerts are sent to the configured SNS topic
- AWS Config rule violations are reported in the AWS Config console
- Checkov scan results are displayed in the deployment output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 
>>>>>>> 054f9d2 (Initial commit)
