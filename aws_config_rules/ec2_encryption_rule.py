import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def evaluate_compliance(configuration_item, rule_parameters):
    """
    Evaluates compliance for EC2 instance encryption
    """
    if configuration_item['resourceType'] != 'AWS::EC2::Instance':
        return {
            'compliance_type': 'NOT_APPLICABLE',
            'annotation': 'The rule does not apply to resources of type ' + configuration_item['resourceType']
        }

    try:
        # Get the configuration details
        configuration = json.loads(configuration_item['configuration'])
        
        # Check if the instance has encryption enabled
        if 'BlockDeviceMappings' in configuration:
            for device in configuration['BlockDeviceMappings']:
                if 'Ebs' in device and 'Encrypted' in device['Ebs']:
                    if device['Ebs']['Encrypted']:
                        return {
                            'compliance_type': 'COMPLIANT',
                            'annotation': 'EC2 instance has encryption enabled'
                        }
                    else:
                        return {
                            'compliance_type': 'NON_COMPLIANT',
                            'annotation': 'EC2 instance does not have encryption enabled'
                        }

        return {
            'compliance_type': 'NON_COMPLIANT',
            'annotation': 'EC2 instance does not have EBS volumes with encryption configuration'
        }

    except Exception as e:
        logger.error(f"Error evaluating compliance: {str(e)}")
        return {
            'compliance_type': 'NON_COMPLIANT',
            'annotation': f'Error evaluating compliance: {str(e)}'
        }

def lambda_handler(event, context):
    """
    Main Lambda handler for AWS Config rule evaluation
    """
    logger.info('Event: %s', json.dumps(event))
    
    invoking_event = json.loads(event['invokingEvent'])
    rule_parameters = json.loads(event.get('ruleParameters', '{}'))
    
    configuration_item = invoking_event['configurationItem']
    
    evaluation = evaluate_compliance(configuration_item, rule_parameters)
    
    config = boto3.client('config')
    response = config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': configuration_item['resourceType'],
                'ComplianceResourceId': configuration_item['resourceId'],
                'ComplianceType': evaluation['compliance_type'],
                'Annotation': evaluation['annotation'],
                'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
            }
        ],
        ResultToken=event['resultToken']
    )
    
    return response 