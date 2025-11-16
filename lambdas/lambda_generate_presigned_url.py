import json
import boto3
import os
import uuid

s3 = boto3.client("s3")
BUCKET = os.environ.get("S3_BUCKET", "alerta-utec")

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    key = f"{uuid.uuid4()}.jpg"  # o el formato que necesites
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=3600
    )
    return response(200, {"key": key, "url": url})