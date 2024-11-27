import boto3
import json
import os

def lambda_handler(event, context):
    print(event)

    try:
        # Analizar el cuerpo de la solicitud
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)

        # Obtener el tenant y id
        tenant_id = body.get('tenant_id')
        user_id = body.get('user_id')

        tabla_usuarios = os.environ["TABLE_NAME_USUARIOS"]
        lambda_token = os.environ["LAMBDA_VALIDAR_TOKEN"]

        # Validar que el tenant y user_id estén presentes
        if not tenant_id and not user_id:
            return {
                'statusCode': 400,
                'status': 'Bad Request - Faltan tenant_id o user_id en la solicitud'
            }
        
        # Inicio - proteger el lambda
        token = event['headers'].get('Authorization', None)
        if not token:
            return {
                'statusCode': 401,
                'status': 'Unauthorized - Falta el token de autorización'
            }

        lambda_client = boto3.client('lambda')
        payload_string = json.dumps(
            {
                "tenant_id": tenant_id,
                "token": token
                })
        invoke_response = lambda_client.invoke(
            FunctionName=lambda_token,
            InvocationType='RequestResponse',
            Payload=payload_string
        )
        response = json.loads(invoke_response['Payload'].read())
        print(response)
        if response['statusCode'] == 403:
            return {
                'statusCode': 403,
                'status': 'Forbidden - Acceso NO Autorizado'
            }

        # Proceso
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tabla_usuarios)
        response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'user_id': user_id
            }
        )

        # Verificar si el producto fue encontrado
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'status': 'Producto no encontrado'
            }

        # Salida (json)
        return {
            'statusCode': 200,
            'response': item
        }
    
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        
        return {
            'statusCode': 500,
            'status': 'Internal Server Error - Ocurrió un error inesperado'
        }