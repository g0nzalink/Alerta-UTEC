import json
import boto3
import os

s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("S3_BUCKET")  # Nombre del bucket desde environment variable

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
        # Manejo seguro de queryStringParameters
        params = event.get("queryStringParameters") or {}
        key = params.get("key")
        
        if not key:
            return response(400, {"error": "Se requiere 'key' como parámetro"})
        
        # Generar URL firmado de S3
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": BUCKET_NAME, "Key": key},
            ExpiresIn=3600  # 1 hora de validez
        )
        return response(200, {"url": url})
    except Exception as e:
        return response(500, {"error": str(e)})