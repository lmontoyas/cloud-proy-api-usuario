import boto3
import hashlib
import uuid # Genera valores únicos
from datetime import datetime, timedelta

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    # Entrada (json)
    tenant_id = event['tenant_id']
    user_id = event['user_id']
    password = event['password']
    hashed_password = hash_password(password)

    # Conectar a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('tp_usuarios')
    
    # Buscar al usuario por user_id
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Usuario no existe'
        }
    
    hashed_password_bd = response['Item']['password']
    if hashed_password != hashed_password_bd:
        return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }
    
    # Genera y guardar token
    token = str(uuid.uuid4())
    fecha_hora_exp = datetime.now() + timedelta(hours=24) # Token válido por 24 horas
    token_table = dynamodb.Table('tp_tokens_acceso')
    registro = {
        'tenant_id': tenant_id,
        'token': token,
        'user_id': user_id,
        'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    token_table.put_item(Item = registro)
            
    
    # Salida (json)
    return {
        'statusCode': 200,
        'token': token,
        'expires_at': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
    }