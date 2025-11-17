import json
import boto3
import uuid
import os
import hmac
import base64
from datetime import datetime, timedelta

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Incidents")
sns_client = boto3.client("sns")
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecreto")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

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
        connections_table = dynamodb.Table("WebSocketConnectionsV2")
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

    # Enviar notificación por email a las autoridades SOLO si es prioridad ALTA
    if item['priority'].lower() == 'high':
        try:
            if SNS_TOPIC_ARN:
                email_subject = f"🚨 URGENTE - Incidente de Prioridad Alta: {item['title']}"
                email_message = f"""
⚠️ ALERTA DE PRIORIDAD ALTA ⚠️

Nuevo incidente URGENTE reportado en Alerta UTEC

Título: {item['title']}
Descripción: {item['description']}
Prioridad: {item['priority'].upper()}
Estado: {item['status']}
Fecha: {item['createdAt']}
ID del Incidente: {item['incidentId']}

⚡ Este incidente requiere atención inmediata.
Por favor, revise el incidente en el sistema lo antes posible.
                """
                
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=email_subject,
                    Message=email_message
                )
                print(f"Notificación SNS enviada para incidente de alta prioridad {incident_id}")
        except Exception as e:
            print(f"Error enviando notificación SNS: {str(e)}")

    # Notificación en tiempo real vía WebSocket
    notify_clients({
        "type": "newIncident",
        "incident": item
    })

    return response(200, item)