import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Incidents")

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

    try:
        res = table.get_item(Key={"incidentId": incident_id})
        item = res.get("Item")
        if not item:
            return response(404, {"message": "Incident not found"})
        return response(200, item)
    except Exception as e:
        return response(500, {"message": str(e)})