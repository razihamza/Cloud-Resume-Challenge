# Lambda function: visitor-counter-function

## Purpose
Receives a POST from API Gateway, adds 1 to the counter in DynamoDB,
and returns `{"visits": <number>}`. Source: `backend/lambda/lambda_function.py`.

## Configuration
| Setting | Value |
|---|---|
| Runtime | Python 3.14 |
| Handler | lambda_function.lambda_handler |
| Memory / timeout | defaults (128 MB / 3 s) |
| Environment variable | TABLE_NAME = visitor-counter |
| Region | ap-south-1 |

## Permissions
The execution role has the basic Lambda logging policy plus this inline policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "dynamodb:UpdateItem",
    "Resource": "arn:aws:dynamodb:ap-south-1:<ACCOUNT_ID>:table/visitor-counter"
  }]
}
```

## Behaviour
- Success: 200 and `{"visits": 43}`
- DynamoDB error: 500 and `{"error": "internal error"}` (details only in logs)

## Test
Test event `{}` in the Lambda console returns 200 with a number.

## Logs
CloudWatch log group `/aws/lambda/visitor-counter-function`, retention 1 month.

## Deploying changes
Manual for now: paste the code, click Deploy. Replaced by the pipeline later.