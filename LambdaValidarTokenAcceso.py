import boto3
from datetime import datetime
import os

def lambda_handler(event, context):
    # Entrada (json)
    tenant_id = event['tenant_id']
    token = event['token']

    tabla_tokens = os.environ["TABLE_NAME_TOKENS_ACCESO"]

    # Conectar a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tabla_tokens)
    
    # Buscar el token en la base de datos
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'token': token
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Token no existe o es inválido para este tenant'
        }
    
    expires = response['Item']['expires']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Verificar si token ha expirado
    if now > expires:
        return {
            'statusCode': 403,
            'body': 'Token expirado'
        }
    
    # Salida (json)
    return {
        'statusCode': 200,
        'body': 'Token válido'
    }