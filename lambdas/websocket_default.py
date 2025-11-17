import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2"))

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        action = body.get("action")
        connection_id = event["requestContext"]["connectionId"]

        # ------- 1. Suscripción a INCIDENTES -------
        if action == "subscribeIncidents":
            table.update_item(
                Key={"connectionId": connection_id},
                UpdateExpression="ADD subscriptions :s",
                ExpressionAttributeValues={
                    ":s": set(["incidents"])
                }
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True, "subscribed": "incidents"})
            }

        # ------- 2. Suscripción a COMMENTS -------
        if action == "subscribeComments":
            table.update_item(
                Key={"connectionId": connection_id},
                UpdateExpression="ADD subscriptions :s",
                ExpressionAttributeValues={
                    ":s": set(["comments"])
                }
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True, "subscribed": "comments"})
            }

        # ------- 3. Enviar mensaje manual (debug) -------
        if action == "sendMessage":
            return {
                "statusCode": 200,
                "body": json.dumps({"message": body.get("message")})
            }

        # ------- 4. Cualquier otra cosa --------
        return {
            "statusCode": 200,
            "body": json.dumps({"info": "default route ok"})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }