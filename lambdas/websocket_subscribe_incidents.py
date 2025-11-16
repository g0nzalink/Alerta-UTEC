import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table("WebSocketConnections")

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event.get("body","{}"))
    # Guardar tipo de suscripción
    connections_table.update_item(
        Key={"connectionId": connection_id},
        UpdateExpression="SET subscriptions = list_append(if_not_exists(subscriptions, :empty), :sub)",
        ExpressionAttributeValues={
            ":sub":[body.get("type","incidents")],
            ":empty":[]
        }
    )
    return {"statusCode":200}