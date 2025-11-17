import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")
connections_table = dynamodb.Table(os.environ["CONNECTIONS_TABLE"])

apigw = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url=os.environ["WS_ENDPOINT"]
)

def lambda_handler(event, context):
    for record in event.get("Records", []):
        if record["eventName"] != "INSERT":
            continue

        new_image = record["dynamodb"].get("NewImage", {})
        if not new_image:
            continue

        incident = {k: list(v.values())[0] for k, v in new_image.items()}

        send_to_subscribers("incidents", incident)

    return {"statusCode": 200}


def send_to_subscribers(subscription_type, payload):
    res = connections_table.scan()

    for item in res.get("Items", []):
        subs = item.get("subscriptions", [])
        conn_id = item["connectionId"]

        if subscription_type not in subs:
            continue

        try:
            apigw.post_to_connection(
                ConnectionId=conn_id,
                Data=json.dumps({
                    "type": subscription_type,
                    "data": payload
                }).encode("utf-8")
            )
        except apigw.exceptions.GoneException:
            # Conexión muerta → se elimina
            connections_table.delete_item(Key={"connectionId": conn_id})
        except Exception as e:
            print("Error enviando mensaje:", str(e))
