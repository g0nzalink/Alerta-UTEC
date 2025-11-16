import boto3
import json
import os

apigw = boto3.client("apigatewaymanagementapi", endpoint_url=os.environ.get("WS_ENDPOINT"))
dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table("WebSocketConnections")

def lambda_handler(event, context):
    body = json.loads(event.get("body","{}"))
    message = body.get("message","")
    
    res = connections_table.scan()
    for item in res.get("Items",[]):
        conn_id = item["connectionId"]
        try:
            apigw.post_to_connection(ConnectionId=conn_id, Data=json.dumps({"message": message}).encode("utf-8"))
        except:
            pass
    return {"statusCode":200}