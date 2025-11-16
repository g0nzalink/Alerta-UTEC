import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Incidents")

def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):

    data = table.scan()

    return response(200, data.get("Items", []))