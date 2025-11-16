import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Comments")  # tabla correcta

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
    # Tomamos el incidentId desde la ruta
    path_params = event.get("pathParameters") or {}
    incident_id = path_params.get("id")

    if not incident_id:
        return response(400, {"error": "Se requiere incidentId en la ruta"})

    try:
        res = table.query(
            KeyConditionExpression=Key("incidentId").eq(incident_id),
            ScanIndexForward=True
        )
        return response(200, res.get("Items", []))
    except Exception as e:
        return response(500, {"error": str(e)})