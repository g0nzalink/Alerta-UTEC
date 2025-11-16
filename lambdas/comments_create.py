import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Comments")  # nombre correcto de la tabla

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

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    # Obtenemos el incidentId desde la ruta
    path_params = event.get("pathParameters") or {}
    incident_id = path_params.get("id")

    if not incident_id:
        return response(400, {"error": "incidentId es requerido en la ruta"})

    if "authorId" not in body or "content" not in body:
        return response(400, {"error": "Se requiere authorId y content en el body"})

    comment_id = str(uuid.uuid4())
    item = {
        "incidentId": incident_id,
        "commentId": comment_id,
        "authorId": body["authorId"],
        "content": body["content"],
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }

    try:
        table.put_item(Item=item)
        return response(200, item)
    except Exception as e:
        return response(500, {"error": str(e)})