import boto3
import json
import os
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")
table = dynamodb.Table(TABLE_NAME)

apig = boto3.client("apigatewaymanagementapi",
    endpoint_url=os.environ["WS_ENDPOINT"]  # ejemplo: "https://xxx.execute-api.us-east-1.amazonaws.com/dev"
)

def send_to_connection(connection_id, message):
    """Envía un mensaje a un cliente específico mediante WebSocket."""
    try:
        apig.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message).encode("utf-8")
        )
    except apig.exceptions.GoneException:
        # La conexión ya no existe → eliminar de DynamoDB
        table.delete_item(Key={"connectionId": connection_id})
    except Exception as e:
        print("Error sending message:", str(e))


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    connection_id = event["requestContext"]["connectionId"]

    # El body puede ser None si el cliente envía un mensaje vacío
    body = event.get("body")
    try:
        data = json.loads(body) if body else {}
    except:
        data = {}

    action = data.get("action")

    # --- 1) NO ACTION → responde algo y termina ---
    if not action:
        send_to_connection(connection_id, {
            "ok": False,
            "error": "Missing 'action' in message"
        })
        return {"statusCode": 200}

    # --- 2) DISPATCH SEGÚN ACTION ---
    if action == "subscribeIncidents":
        return handle_subscribe(connection_id, "incidents")

    if action == "subscribeComments":
        return handle_subscribe(connection_id, "comments")

    if action == "subscribeNotify":
        return handle_subscribe(connection_id, "notify")

    if action == "sendMessage":
        return handle_send_message(connection_id, data)

    # --- 3) ACTION DESCONOCIDA ---
    send_to_connection(connection_id, {
        "ok": False,
        "error": f"Unknown action '{action}'"
    })
    return {"statusCode": 200}


# ============================================================
# HANDLERS DE ACCIONES
# ============================================================

def handle_subscribe(connection_id, sub_type):
    """Suscribe a un cliente a un tipo de evento."""
    try:
        # Actualiza la lista de suscripciones sin sobrescribir datos existentes
        table.update_item(
            Key={"connectionId": connection_id},
            UpdateExpression="ADD subscriptions :s SET lastSeen = :now",
            ExpressionAttributeValues={
                ":s": set([sub_type]),
                ":now": datetime.utcnow().isoformat()
            }
        )

        send_to_connection(connection_id, {
            "ok": True,
            "subscribed": sub_type
        })

    except Exception as e:
        print("Subscribe error:", str(e))
        send_to_connection(connection_id, {
            "ok": False,
            "error": "Subscription error"
        })

    return {"statusCode": 200}


def handle_send_message(connection_id, data):
    """Echo básico para probar WebSocket."""
    msg = data.get("message", "")
    send_to_connection(connection_id, {
        "echo": msg,
        "from": connection_id
    })
    return {"statusCode": 200}