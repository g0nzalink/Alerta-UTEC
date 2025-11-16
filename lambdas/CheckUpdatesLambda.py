import boto3
import json
import os
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
incidents_table = dynamodb.Table(os.environ.get("INCIDENTS_TABLE", "Incidents"))
connections_table = dynamodb.Table("WebSocketConnections")

def lambda_handler(event, context):
    """
    Lambda programada que verifica actualizaciones en incidentes
    y notifica a través de WebSocket a los clientes suscritos.
    """
    try:
        # Obtener el endpoint de WebSocket
        ws_endpoint = os.environ.get("WS_ENDPOINT")
        if not ws_endpoint:
            print("WS_ENDPOINT no configurado")
            return {"statusCode": 500, "body": "WS_ENDPOINT not configured"}
        
        apigw = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=ws_endpoint
        )
        
        # Escanear incidentes recientes (últimos 5 minutos)
        # En producción, considera usar GSI con timestamp
        response = incidents_table.scan()
        incidents = response.get("Items", [])
        
        # Obtener conexiones activas
        connections_response = connections_table.scan()
        connections = connections_response.get("Items", [])
        
        # Enviar actualizaciones a clientes suscritos
        stale_connections = []
        for connection in connections:
            connection_id = connection.get("connectionId")
            subscriptions = connection.get("subscriptions", set())
            
            # Verificar si está suscrito a incidentes
            if "incidents" in subscriptions:
                try:
                    message = {
                        "type": "incident_update",
                        "data": {
                            "count": len(incidents),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    apigw.post_to_connection(
                        ConnectionId=connection_id,
                        Data=json.dumps(message).encode("utf-8")
                    )
                except apigw.exceptions.GoneException:
                    # Conexión obsoleta, marcar para eliminación
                    stale_connections.append(connection_id)
                except Exception as e:
                    print(f"Error enviando a {connection_id}: {str(e)}")
        
        # Limpiar conexiones obsoletas
        for conn_id in stale_connections:
            try:
                connections_table.delete_item(Key={"connectionId": conn_id})
            except Exception as e:
                print(f"Error eliminando conexión {conn_id}: {str(e)}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Updates checked",
                "incidents_count": len(incidents),
                "connections_notified": len(connections) - len(stale_connections),
                "stale_connections_removed": len(stale_connections)
            })
        }
        
    except Exception as e:
        print(f"Error en CheckUpdatesLambda: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
