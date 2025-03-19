import boto3
import json
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define required tags
REQUIRED_TAGS = {
    'Environment': ['Production', 'Development', 'Staging'],
    'Project': None,  # Any value is acceptable
    'Owner': None,
    'CostCenter': None
}

def check_resource_tags(resource_arn, resource_type):
    """
    Check if a resource has all required tags
    """
    try:
        # Get the resource tags
        resource = boto3.client('resourcegroupstaggingapi')
        response = resource.get_resources(
            ResourceARNList=[resource_arn]
        )
        
        if not response['ResourceTagMappingList']:
            return False, "No tags found on resource"
            
        tags = {tag['Key']: tag['Value'] for tag in response['ResourceTagMappingList'][0]['Tags']}
        
        # Check each required tag
        missing_tags = []
        invalid_tags = []
        
        for tag_key, allowed_values in REQUIRED_TAGS.items():
            if tag_key not in tags:
                missing_tags.append(tag_key)
            elif allowed_values and tags[tag_key] not in allowed_values:
                invalid_tags.append(f"{tag_key}: {tags[tag_key]} (allowed values: {', '.join(allowed_values)})")
        
        if missing_tags or invalid_tags:
            return False, {
                'missing_tags': missing_tags,
                'invalid_tags': invalid_tags
            }
            
        return True, "All required tags are present and valid"
        
    except Exception as e:
        logger.error(f"Error checking tags for {resource_arn}: {str(e)}")
        return False, f"Error checking tags: {str(e)}"

def send_alert(resource_arn, resource_type, compliance_status, details):
    """
    Send alert for non-compliant resources
    """
    try:
        sns = boto3.client('sns')
        topic_arn = 'arn:aws:sns:region:account-id:tag-compliance-alerts'  # Replace with your SNS topic ARN
        
        message = {
            'timestamp': datetime.utcnow().isoformat(),
            'resource_arn': resource_arn,
            'resource_type': resource_type,
            'compliance_status': compliance_status,
            'details': details
        }
        
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=f"Tag Compliance Alert - {resource_type}"
        )
        
    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")

def lambda_handler(event, context):
    """
    Main Lambda handler for tag enforcement
    """
    logger.info('Event: %s', json.dumps(event))
    
    try:
        # Process each resource in the event
        for record in event['Records']:
            resource_arn = record['Sns']['Message']
            resource_type = resource_arn.split(':')[2]  # Extract resource type from ARN
            
            is_compliant, details = check_resource_tags(resource_arn, resource_type)
            
            if not is_compliant:
                send_alert(resource_arn, resource_type, 'NON_COMPLIANT', details)
                
        return {
            'statusCode': 200,
            'body': json.dumps('Tag enforcement check completed')
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        } 