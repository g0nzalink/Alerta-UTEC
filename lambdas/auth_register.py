import json
import boto3
import uuid
import hashlib
import os
import hmac
import base64
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr  # IMPORT CORRECTO PARA SCAN

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Users")
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecreto")

def hash_password(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body)
    }

def create_jwt(payload, secret, exp_hours=12):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = payload.copy()
    payload["exp"] = int((datetime.utcnow() + timedelta(hours=exp_hours)).timestamp())

    def b64encode(obj):
        return base64.urlsafe_b64encode(json.dumps(obj, separators=(',', ':')).encode()).rstrip(b"=")

    header_enc = b64encode(header)
    payload_enc = b64encode(payload)
    signature = hmac.new(secret.encode(), header_enc + b"." + payload_enc, hashlib.sha256).digest()
    signature_enc = base64.urlsafe_b64encode(signature).rstrip(b"=")
    return b".".join([header_enc, payload_enc, signature_enc]).decode()

def lambda_handler(event, context):
    body = json.loads(event["body"])
    email = body["email"]
    password = body["password"]
    role = body.get("role", "USER")  # default USER

    # Verificar si ya existe
    existing = table.scan(
        FilterExpression=Attr("email").eq(email)
    ).get("Items", [])
    if existing:
        return response(400, {"error": "Usuario ya existe"})

    # Crear usuario
    user_id = str(uuid.uuid4())
    item = {
        "userId": user_id,
        "email": email,
        "passwordHash": hash_password(password),
        "role": role,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)

    # Generar token JWT usando nuestra función interna
    token = create_jwt({"userId": user_id, "role": role}, JWT_SECRET)

    return response(200, {"token": token})