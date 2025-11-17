import boto3
import json
import os
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        # Optionally extract a user identifier from queryStringParameters or headers if you send a token
        user_id = None
        qs = event.get("queryStringParameters") or {}
        if qs and "userId" in qs:
            user_id = qs.get("userId")

        item = {
            "connectionId": connection_id,
            "connectedAt": datetime.utcnow().isoformat(),
            "lastSeen": datetime.utcnow().isoformat()
        }
        if user_id:
            item["userId"] = user_id

        # Do NOT write an empty set to DynamoDB (empty sets are not allowed).
        # We avoid creating a "subscriptions" attribute here; it will be added when client subscribes.
        table.put_item(Item=item)
        return {"statusCode": 200}
    except Exception as e:
        print(f"Error connecting: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}