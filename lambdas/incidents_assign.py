import json
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Incidents")

def response(status, body):
    return {"statusCode": status,"headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},"body": json.dumps(body)}

def lambda_handler(event, context):
    incident_id = event["pathParameters"]["id"]
    body = json.loads(event.get("body", "{}"))
    assigned_user = body.get("userId")
    if not assigned_user:
        return response(400, {"error": "userId requerido"})

    res = table.update_item(
        Key={"PK": f"INCIDENT#{incident_id}", "SK": "METADATA"},
        UpdateExpression="SET assignedTo = :a, updatedAt = :u",
        ExpressionAttributeValues={
            ":a": assigned_user,
            ":u": datetime.utcnow().isoformat()
        },
        ReturnValues="ALL_NEW"
    )
    return response(200, res.get("Attributes", {}))