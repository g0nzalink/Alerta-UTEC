import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        table.delete_item(Key={"connectionId": connection_id})
        return {"statusCode": 200}
    except Exception as e:
        print(f"Error disconnecting: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
