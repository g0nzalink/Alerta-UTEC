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

        # Parsear body
        body = json.loads(event.get("body", "{}"))

        # Acción esperada
        action = body.get("action")
        if action != "subscribeIncidents":
            return {
                "statusCode": 400,
                "body": json.dumps({"ok": False, "error": "Missing or invalid action"})
            }

        # Tipo de suscripción
        subscription_type = "incidents"

        # Guardar en DynamoDB (crea lista si no existe)
        connections_table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="""
                SET subscriptions = list_append(if_not_exists(subscriptions, :empty), :sub)
            """,
            ExpressionAttributeValues={
                ":empty": [],
                ":sub": [subscription_type]
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True, "subscribed": subscription_type})
        }

    except Exception as e:
        print("ERROR in subscribeIncidents:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e)})
        }