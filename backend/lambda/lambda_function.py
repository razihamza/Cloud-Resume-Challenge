import json
import os

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        response = table.update_item(
            Key={"id": "resume-site"},
            UpdateExpression="ADD #v :inc",
            ExpressionAttributeNames={"#v": "visits"},
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW",
        )
        visits = int(response["Attributes"]["visits"])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"visits": visits}),
        }
    except ClientError as err:
        print("DynamoDB error:", err)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "internal error"}),
        }