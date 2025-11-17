import boto3
import json

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table("WebSocketConnectionsV2")

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        body = json.loads(event.get("body", "{}"))
        
        # Agregar suscripción "comments" usando StringSet
        connections_table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="ADD subscriptions :sub",
            ExpressionAttributeValues={
                ":sub": {"comments"}
            }
        )
        
        return {"statusCode": 200, "body": json.dumps({"message": "Suscrito a comentarios"})}
    except Exception as e:
        print(f"Error subscribing to comments: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}