import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("WebSocketConnections")

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        table.put_item(Item={
            "connectionId": connection_id,
            "subscriptions": set()
        })
        return {"statusCode": 200}
    except Exception as e:
        print(f"Error connecting: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}