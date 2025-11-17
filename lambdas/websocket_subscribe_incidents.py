import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")

# IMPORTANTE:
# Usa SIEMPRE la misma variable que definiste en serverless.yml
CONNECTIONS_TABLE = os.environ["ConnectionsTable"]
table = dynamodb.Table(CONNECTIONS_TABLE)

def lambda_handler(event, context):
    try:
        print("DEBUG subscribeIncidents EVENT:", json.dumps(event))

        connection_id = event["requestContext"]["connectionId"]

        # Guardar conexión con tipo "incidents"
        table.put_item(
            Item={
                "connectionId": connection_id,
                "type": "incidents"
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "ok": True,
                "subscribed": "incidents"
            })
        }

    except Exception as e:
        print("ERROR subscribeIncidents:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e)})
        }