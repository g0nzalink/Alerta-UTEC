# Alerta UTEC – Backend Serverless (AWS)

Este backend implementa la aplicación “Alerta UTEC” utilizando una arquitectura completamente **serverless** montada sobre AWS. El proyecto usa **API Gateway**, **AWS Lambda**, **DynamoDB**, **S3**, **WebSockets**, y está gestionado mediante el framework **Serverless**.  
El objetivo es ofrecer un sistema de reportes de incidentes dentro del campus, con autenticación, gestión de comentarios, notificaciones y actualizaciones en tiempo real.

---

## Tecnologías principales

- AWS Lambda (Python 3.11)
- Amazon API Gateway (REST + WebSocket)
- DynamoDB (Incidents, Comments, Users, Notifications, WebSocketConnections)
- Amazon S3 (almacenamiento de imágenes)
- Serverless Framework v3
- JWT Authentication
- WebSockets para actualizaciones en tiempo real

---

## Arquitectura general

El proyecto sigue una arquitectura por funciones Lambda independientes, cada una manejando un endpoint o evento específico. La base del sistema es el archivo `serverless.yml`, que define toda la infraestructura: funciones, tablas, streams, bucket S3 y API Gateway.

### Estructura del proyecto

.
├── serverless.yml
├── requirements.txt
└── lambdas/
├── auth_register.py
├── auth_login.py
├── incidents_create.py
├── incidents_list.py
├── incidents_get.py
├── incidents_update.py
├── incidents_assign.py
├── comments_create.py
├── comments_list.py
├── notifications_list.py
├── notifications_mark_read.py
├── admin_list.py
├── images_getSignedUrl.py
├── lambda_generate_presigned_url.py
├── websocket_connect.py
├── websocket_disconnect.py
├── websocket_default.py
├── websocket_subscribe_incidents.py
├── websocket_subscribe_comments.py
├── websocket_subscribe_notify.py
├── IncidentsStreamProcessor.py
├── CommentsStreamProcessor.py
└── CheckUpdatesLambda.py

---

## Tablas DynamoDB

El backend utiliza las siguientes tablas:

- **Users**  
  Almacena usuarios, roles y datos básicos para autenticación.
- **Incidents**  
  Reportes creados por los usuarios.
- **Comments**  
  Comentarios asociados a incidentes.
- **Notifications**  
  Notificaciones generadas (actualmente en desuso).
- **WebSocketConnections**  
  Conexiones activas para envío en tiempo real.
- **(Streams activos en Incidents y Comments)**  
  Usados para notificaciones en tiempo real vía WebSockets.

---

## Endpoints REST

Base URL: https://nal0woodc6.execute-api.us-east-1.amazonaws.com/dev


---

### 1. Autenticación

| Método | Endpoint | Descripción |
|-------|----------|-------------|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Iniciar sesión y obtener JWT |

---

### 2. Incidentes

| Método | Endpoint | Descripción |
|-------|----------|-------------|
| POST | `/incidents` | Crear incidente |
| GET | `/incidents` | Listar incidentes |
| GET | `/incidents/{id}` | Obtener incidente |
| PUT | `/incidents/{id}` | Actualizar incidente |
| POST | `/incidents/{id}/assign` | **En desuso** |

---

### 3. Comentarios

| Método | Endpoint | Descripción |
|-------|----------|-------------|
| POST | `/incidents/{id}/comments` | Crear comentario |
| GET | `/incidents/{id}/comments` | Listar comentarios |

---

### 4. Notificaciones (en desuso)

| Método | Endpoint | Descripción |
|-------|----------|-------------|
| GET | `/notifications` | Listar notificaciones |
| PUT | `/notifications/{id}/mark-read` | Marcar como leída |

> Actualmente reemplazado por WebSockets + DynamoDB Streams.

---

### 5. Administración

| Método | Endpoint | Descripción |
|-------|----------|-------------|
| GET | `/users/admin-status` | Validar si usuario es admin |

---

### 6. Imágenes (con errores)

| Método | Endpoint | Estado |
|-------|----------|--------|
| GET | `/images/signed-url` | Presenta errores |
| POST | `/images/generate` | Presenta errores |

---

## WebSockets

Base WebSocket:

Rutas disponibles:

- `$connect`
- `$disconnect`
- `$default`
- `subscribeIncidents`
- `subscribeComments`
- `subscribeNotify`

Streams procesados:

- IncidentsStreamProcessor  
- CommentsStreamProcessor  
- CheckUpdatesLambda  

---

# Lista de Lambdas desplegadas

auth_register
auth_login
incidents_create
incidents_list
incidents_get
incidents_update
incidents_assign (en desuso)
comments_create
comments_list
notifications_list (en desuso)
notifications_mark_read (en desuso)
admin_list
images_getSignedUrl (con errores)
lambda_generate_presigned_url (con errores)

websocket_connect
websocket_disconnect
websocket_default
websocket_subscribe_incidents
websocket_subscribe_comments
websocket_subscribe_notify

IncidentsStreamProcessor
CommentsStreamProcessor
CheckUpdatesLambda


---

# Instalación local

### 1. Configurar AWS CLI

aws configure

### 2. Desplegar

sls deploy


Esto generará:

- API Gateway REST  
- API Gateway WebSocket  
- Lambdas  
- DynamoDB  
- Bucket S3  
- Roles IAM  

---

# Notas importantes

- Los endpoints **incidents/assign**, **notifications** y **mark-read** están **en desuso**.  
- Los endpoints relacionados a **imágenes** no funcionan debido a errores en políticas S3/IAM.  
- Las actualizaciones en tiempo real funcionan mediante **WebSockets + DynamoDB Streams**, no mediante REST.  

---