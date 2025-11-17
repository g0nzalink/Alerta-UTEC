import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")
connections_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        # Add subscription as a String Set (boto3 resource accepts Python set -> DynamoDB SS)
        connections_table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="ADD subscriptions :sub",
            ExpressionAttributeValues={
                ":sub": set(["comments"])
            }
        )
        return {"statusCode": 200, "body": json.dumps({"message": "Suscrito a comentarios"})}
    except Exception as e:
        print(f"Error subscribing to comments: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}