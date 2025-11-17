import boto3
import json
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
CONN_TABLE = os.environ.get("CONNECTIONS_TABLE", "WebSocketConnections")
connections_table = dynamodb.Table(CONN_TABLE)

# Cliente WebSocket fijo basado en variable de entorno
def get_ws_client():
    endpoint = os.environ["WS_ENDPOINT"]  # wss://xxxx.execute-api.us-east-1.amazonaws.com/dev
    # Convertimos wss:// en https:// porque el SDK usa HTTPS
    endpoint = endpoint.replace("wss://", "https://")
    return boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)


def lambda_handler(event, context):
    print("Event received:", event)

    try:
        body = json.loads(event.get("body", "{}"))
    except:
        body = {}

    message = body.get("message", "")
    if not message:
        return {"statusCode": 400, "body": "Missing message"}

    ws = get_ws_client()

    # Scan en la tabla para enviar a todos
    try:
        response = connections_table.scan()
        items = response.get("Items", [])

        for item in items:
            conn_id = item["connectionId"]

            try:
                ws.post_to_connection(
                    ConnectionId=conn_id,
                    Data=json.dumps({"message": message}).encode("utf-8")
                )
            except ClientError as e:
                # Si la conexión ya murió → eliminar de la tabla
                if e.response["Error"]["Code"] in ("GoneException", "410"):
                    connections_table.delete_item(Key={"connectionId": conn_id})
                else:
                    print("Error enviando a", conn_id, e)

    except Exception as e:
        print("Error en scan:", e)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    return {"statusCode": 200, "body": json.dumps({"sent": True})}