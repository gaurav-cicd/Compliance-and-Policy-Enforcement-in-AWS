import boto3
import sys
import json

def validate_config_rules():
    """
    Validates AWS Config rules before deployment
    """
    try:
        config = boto3.client('config')
        
        # Get existing rules
        response = config.describe_config_rules()
        existing_rules = {rule['ConfigRuleName'] for rule in response['ConfigRules']}
        
        # Check if our rule exists
        rule_name = 'ec2-encryption-rule'
        if rule_name in existing_rules:
            print(f"Config rule '{rule_name}' already exists")
            return True
            
        # Validate rule configuration
        with open('ec2_encryption_rule.py', 'r') as f:
            rule_code = f.read()
            
        # Basic validation checks
        if 'evaluate_compliance' not in rule_code:
            print("Error: Rule code missing evaluate_compliance function")
            return False
            
        if 'lambda_handler' not in rule_code:
            print("Error: Rule code missing lambda_handler function")
            return False
            
        print("AWS Config rule validation successful")
        return True
        
    except Exception as e:
        print(f"Error validating AWS Config rules: {str(e)}")
        return False

if __name__ == "__main__":
    if not validate_config_rules():
        sys.exit(1) 