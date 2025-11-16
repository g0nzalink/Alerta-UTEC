import json
import boto3
import uuid
import os
import hmac
import base64
from datetime import datetime, timedelta

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Incidents")
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecreto")

apigw = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url="https://nkhi26ts7h.execute-api.us-east-1.amazonaws.com/dev/@connections"
)

def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps(body)
    }

def decode_jwt(token, secret):
    """Decodificación simple JWT sin librerías externas"""
    try:
        header_enc, payload_enc, signature_enc = token.split(".")
        payload = json.loads(base64.urlsafe_b64decode(payload_enc + "=="))
        return payload
    except Exception:
        return None

def notify_clients(message):
    """Notifica a todos los clientes suscritos (simplificado)"""
    try:
        connections_table = dynamodb.Table("WebSocketConnections")
        response_scan = connections_table.scan()
        for item in response_scan.get("Items", []):
            conn_id = item["connectionId"]
            try:
                apigw.post_to_connection(
                    ConnectionId=conn_id,
                    Data=json.dumps(message).encode("utf-8")
                )
            except Exception as e:
                print(f"No se pudo notificar a {conn_id}: {str(e)}")
    except Exception as e:
        print("Error al notificar clientes:", str(e))

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    # Obtener token del header Authorization
    auth_header = event.get("headers", {}).get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return response(401, {"error": "Token no proporcionado"})
    token = auth_header.split(" ")[1]
    claims = decode_jwt(token, JWT_SECRET)
    if not claims or "userId" not in claims:
        return response(401, {"error": "Token inválido"})

    author_id = claims["userId"]

    incident_id = str(uuid.uuid4())
    item = {
        "PK": f"INCIDENT#{incident_id}",
        "SK": "METADATA",
        "incidentId": incident_id,
        "title": body.get("title", ""),
        "description": body.get("description", ""),
        "priority": body.get("priority", "low"),
        "status": "open",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "images": body.get("images", []),
        "authorId": author_id
    }

    table.put_item(Item=item)

    # Notificación en tiempo real vía WebSocket
    notify_clients({
        "type": "newIncident",
        "incident": item
    })

    return response(200, item)