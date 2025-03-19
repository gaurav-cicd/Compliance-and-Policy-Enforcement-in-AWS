import json
import sys
from datetime import datetime

def validate_tag_policies():
    """
    Validates tag policies before deployment
    """
    try:
        # Read the tag enforcement code
        with open('tag_enforcement.py', 'r') as f:
            code = f.read()
            
        # Validate required components
        required_components = [
            'REQUIRED_TAGS',
            'check_resource_tags',
            'send_alert',
            'lambda_handler'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in code:
                missing_components.append(component)
                
        if missing_components:
            print(f"Error: Missing required components: {', '.join(missing_components)}")
            return False
            
        # Validate tag structure
        if 'REQUIRED_TAGS' in code:
            # Basic structure validation
            if not isinstance(eval(code.split('REQUIRED_TAGS = ')[1].split('\n')[0]), dict):
                print("Error: REQUIRED_TAGS must be a dictionary")
                return False
                
        print("Tag policy validation successful")
        return True
        
    except Exception as e:
        print(f"Error validating tag policies: {str(e)}")
        return False

if __name__ == "__main__":
    if not validate_tag_policies():
        sys.exit(1) 