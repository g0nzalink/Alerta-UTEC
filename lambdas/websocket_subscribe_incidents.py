import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")
connections_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    print("DEBUG subscribeIncidents EVENT:", json.dumps(event))
    try:
        connection_id = event["requestContext"]["connectionId"]
        body = json.loads(event.get("body","{}"))
        subscription_type = body.get("type", "incidents")
        connections_table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="ADD subscriptions :sub",
            ExpressionAttributeValues={
                ":sub": set([subscription_type])
            }
        )
        return {"statusCode": 200, "body": json.dumps({"message": f"Suscrito a {subscription_type}"})}
    except Exception as e:
        print(f"Error subscribing to incidents: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}