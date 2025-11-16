import boto3
import json

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table("WebSocketConnections")

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event.get("body", "{}"))
    
    # Guardar tipo de suscripción "notifications"
    connections_table.update_item(
        Key={"connectionId": connection_id},
        UpdateExpression="SET subscriptions = list_append(if_not_exists(subscriptions, :empty), :sub)",
        ExpressionAttributeValues={
            ":sub": ["notifications"],
            ":empty": []
        }
    )
    
    return {"statusCode": 200, "body": json.dumps({"message": "Suscrito a notificaciones"})}