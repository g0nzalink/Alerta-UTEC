import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Users")  # Nombre correcto de tu tabla de usuarios

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
    try:
        # Filtramos solo usuarios con rol de personal administrativo
        res = table.scan(
            FilterExpression="#r = :staff",
            ExpressionAttributeNames={"#r": "role"},
            ExpressionAttributeValues={":staff": "STAFF"}  # Ajusta al valor exacto que uses en tu tabla
        )
        staff_users = res.get("Items", [])
        return response(200, staff_users)
    except Exception as e:
        return response(500, {"error": str(e)})