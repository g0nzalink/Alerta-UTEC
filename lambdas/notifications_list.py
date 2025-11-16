import json
import boto3
from boto3.dynamodb.conditions import Key
import base64
import hmac
import hashlib
import os

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Notifications")
JWT_SECRET = os.environ.get("JWT_SECRET")

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
        "body": json.dumps(body)
    }

def decode_jwt(token, secret=JWT_SECRET):
    try:
        header_enc, payload_enc, signature_enc = token.split(".")
        payload_bytes = base64.urlsafe_b64decode(payload_enc + "==")
        payload = json.loads(payload_bytes)
        signature_check = hmac.new(secret.encode(), f"{header_enc}.{payload_enc}".encode(), hashlib.sha256).digest()
        signature_check_enc = base64.urlsafe_b64encode(signature_check).rstrip(b"=").decode()
        if signature_check_enc != signature_enc:
            return None
        return payload
    except:
        return None

def lambda_handler(event, context):
    auth_header = event.get("headers", {}).get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return response(401, {"error": "Token requerido"})
    token = auth_header.split(" ")[1]
    claims = decode_jwt(token)
    if not claims or "userId" not in claims:
        return response(401, {"error": "Token inválido"})

    user_id = claims["userId"]

    res = table.query(
        KeyConditionExpression=Key("userId").eq(user_id)
    )

    return response(200, res.get("Items", []))