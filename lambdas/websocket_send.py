import boto3
import json
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
CONN_TABLE = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnectionsV2")
connections_table = dynamodb.Table(CONN_TABLE)

def make_apigw_client(event):
    domain = event["requestContext"].get("domainName")
    stage = event["requestContext"].get("stage")
    endpoint = f"https://{domain}/{stage}"
    return boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)

def lambda_handler(event, context):
    body = event.get("body") or "{}"
    try:
        payload = json.loads(body)
    except:
        payload = {"message": str(body)}

    message = payload.get("message", "")

    apigw = make_apigw_client(event)

    # Basic broadcast: we filter only connections that have at least one subscription attribute
    # This avoids trying to send to entries without subscription attr.
    try:
        scan_kwargs = {
            "ProjectionExpression": "connectionId, subscriptions"
        }
        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            res = connections_table.scan(**scan_kwargs)
            items = res.get('Items', [])
            for item in items:
                conn_id = item.get('connectionId')
                # Optionally filter by subscription here (if you want to send only to certain topics)
                # e.g., if payload.get("topic") and payload["topic"] not in item.get("subscriptions", []): continue
                try:
                    apigw.post_to_connection(ConnectionId=conn_id, Data=json.dumps({"message": message}).encode('utf-8'))
                except ClientError as e:
                    err_code = e.response.get("Error", {}).get("Code")
                    # If connection is gone, delete it
                    if err_code == 'GoneException' or e.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 410:
                        try:
                            connections_table.delete_item(Key={"connectionId": conn_id})
                        except Exception as de:
                            print("Error deleting stale connection:", de)
                    else:
                        print(f"Error posting to {conn_id}: {e}")
            start_key = res.get('LastEvaluatedKey', None)
            done = start_key is None
    except Exception as e:
        print("Error scanning connections table:", e)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    return {"statusCode": 200, "body": json.dumps({"sent": True})}