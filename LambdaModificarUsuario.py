import boto3
import json
import os

def lambdahandler(event, context):
    print(event)
    try:
        # Obtener el dni, password y datos del usuario
        tenant_id = event['tenant_id']
        user_id = event['user_id']
        email = event['email']
        nombre = event['nombre']
        apell_pat = event['apell_pat']
        apell_mat = event['apell_mat']

        tabla_usuarios = os.environ["TABLE_NAME_USUARIOS"]

        if not tenant_id and not user_id:
            return {
                'statusCode': 400,
                'status': 'Bad Request - Falta tenant_id o user_id'
            }

        # Inicio - Proteger el lambda
        token = event['headers']['Authorization']
        if not token:
            return {
                'statusCode': 401,
                'status': 'Unauthorized - Falta token de autorización'
            }
        
        lambda_client = boto3.client('lambda')
        payload_string = json.dumps({'token': token})
        invoke_response = lambda_client.invoke(
            FunctionName = 'ValidarTokenAcceso',
            InvocationType = 'RequestResponse',
            Payload = payload_string
        )

        response = json.loads(invoke_response['Payload'].read())
        print(response)

        if response['statusCode'] == 403:
            return {
                'statusCode': 403,
                'status': 'Forbidden - Acceso NO autorizado'
            }
        
        #Proceso
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tabla_usuarios)
        response = table.update_item(
            key = {
                'tenant_id': tenant_id,
                'user_id': user_id
            },
            UpdateExpression = 'set nombre=:nombre, email=:email, apell_pat=:apell_pat, apell_mat=:apell_mat',
            ExpressionAttributeValues = {
                ':nombre': nombre,
                ':email': email,
                ':apell_pat': apell_pat,
                ':apell_mat': apell_mat
            },
            ReturnValues = 'UPDATED_NEW'
        )

        return {
            'statusCode': 200,
            'response': response
        }
    
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        
        return {
            'statusCode': 500,
            'status': 'Internal Server Error - Ocurrió un error inesperado'
        }
        