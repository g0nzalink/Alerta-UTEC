import boto3
import json
import os

dynamodb = boto3.client("dynamodb")
TABLE = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        action = body.get("action")
        connection_id = event["requestContext"]["connectionId"]

        # ------- 1. Suscripción a INCIDENTES -------
        if action == "subscribeIncidents":
            dynamodb.update_item(
                TableName=TABLE,
                Key={"connectionId": {"S": connection_id}},
                UpdateExpression="ADD subscriptions :s",
                ExpressionAttributeValues={
                    ":s": {"SS": ["incidents"]}
                }
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True, "subscribed": "incidents"})
            }

        # ------- 2. Suscripción a COMMENTS -------
        if action == "subscribeComments":
            dynamodb.update_item(
                TableName=TABLE,
                Key={"connectionId": {"S": connection_id}},
                UpdateExpression="ADD subscriptions :s",
                ExpressionAttributeValues={
                    ":s": {"SS": ["comments"]}
                }
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True, "subscribed": "comments"})
            }

        # ------- 3. Enviar mensajes (debug) -------
        if action == "sendMessage":
            return {
                "statusCode": 200,
                "body": json.dumps({"message": body.get("message")})
            }

        return {"statusCode": 200, "body": "default-ok"}

    except Exception as e:
        print("ERROR IN DEFAULT:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}