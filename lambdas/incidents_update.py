import json
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Incidents")  # tabla correcta

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
    incident_id = event["pathParameters"]["id"]
    body = json.loads(event["body"])

    update_expression = "SET updatedAt = :updatedAt"
    expression_values = {":updatedAt": datetime.utcnow().isoformat()}
    expression_names = {}

    # Manejo de campos opcionales
    if "title" in body:
        update_expression += ", title = :title"
        expression_values[":title"] = body["title"]

    if "description" in body:
        update_expression += ", description = :description"
        expression_values[":description"] = body["description"]

    if "priority" in body:
        update_expression += ", priority = :priority"
        expression_values[":priority"] = body["priority"]

    if "status" in body:
        update_expression += ", #s = :status"
        expression_values[":status"] = body["status"]
        expression_names["#s"] = "status"  # alias para palabra reservada

    if "images" in body:
        update_expression += ", images = :images"
        expression_values[":images"] = body["images"]

    try:
        table.update_item(
            Key={"incidentId": incident_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names if expression_names else None,
            ReturnValues="ALL_NEW"
        )

        # Recuperar el item actualizado
        updated_item = table.get_item(Key={"incidentId": incident_id}).get("Item")
        return response(200, updated_item)

    except Exception as e:
        return response(500, {"message": str(e)})