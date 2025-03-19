terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Pre-apply hook for compliance checks
resource "null_resource" "pre_apply_checks" {
  triggers = {
    # Run on every apply
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command = "chmod +x pre-apply-hook.sh && ./pre-apply-hook.sh"
  }
}

# SNS Topic for tag compliance alerts
resource "aws_sns_topic" "tag_compliance_alerts" {
  name = "tag-compliance-alerts"
  depends_on = [null_resource.pre_apply_checks]
}

# Lambda function for tag enforcement
resource "aws_lambda_function" "tag_enforcement" {
  filename         = "../lambda_functions/tag_enforcement.zip"
  function_name    = "tag-enforcement"
  role            = aws_iam_role.lambda_role.arn
  handler         = "tag_enforcement.lambda_handler"
  runtime         = "python3.8"
  timeout         = 300
  memory_size     = 256
  source_code_hash = filebase64sha256("../lambda_functions/tag_enforcement.zip")
  depends_on = [null_resource.pre_apply_checks]

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.tag_compliance_alerts.arn
    }
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "tag-enforcement-lambda-role"
  depends_on = [null_resource.pre_apply_checks]

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "tag-enforcement-lambda-policy"
  role = aws_iam_role.lambda_role.id
  depends_on = [null_resource.pre_apply_checks]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "resourcegroupstaggingapi:GetResources",
          "sns:Publish"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# CloudWatch Event rule to trigger Lambda
resource "aws_cloudwatch_event_rule" "tag_check_schedule" {
  name                = "tag-check-schedule"
  description         = "Schedule for tag compliance checks"
  schedule_expression = "rate(1 hour)"
  depends_on = [null_resource.pre_apply_checks]
}

# CloudWatch Event target
resource "aws_cloudwatch_event_target" "tag_check_target" {
  rule      = aws_cloudwatch_event_rule.tag_check_schedule.name
  target_id = "TagEnforcementLambda"
  arn       = aws_lambda_function.tag_enforcement.arn
  depends_on = [null_resource.pre_apply_checks]
}

# Lambda permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tag_enforcement.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.tag_check_schedule.arn
  depends_on = [null_resource.pre_apply_checks]
} 