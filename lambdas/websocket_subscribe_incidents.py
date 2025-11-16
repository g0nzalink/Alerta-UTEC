import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table("WebSocketConnections")

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        body = json.loads(event.get("body","{}"))
        
        # Agregar tipo de suscripción usando StringSet
        subscription_type = body.get("type", "incidents")
        connections_table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="ADD subscriptions :sub",
            ExpressionAttributeValues={
                ":sub": {subscription_type}
            }
        )
        
        return {"statusCode": 200, "body": json.dumps({"message": f"Suscrito a {subscription_type}"})}
    except Exception as e:
        print(f"Error subscribing to incidents: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}