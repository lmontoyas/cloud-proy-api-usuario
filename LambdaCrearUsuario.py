import boto3
import hashlib
import json
import os

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

# Función que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        # Imprimir el evento para depuración
        print("Evento recibido:", event)

        # Analizar el cuerpo de la solicitud
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)

        # Obtener el dni, password y datos del usuario
        tenant_id = body.get('tenant_id')
        user_id = body.get('user_id')
        email = body.get('email')
        nombre = body.get('nombre')
        apell_pat = body.get('apell_pat')
        apell_mat = body.get('apell_mat')
        password = body.get('password')

        if email == 'aldair.seminario@utec.edu.pe':
            rol = 'developer'
        else:
            rol = 'client'

        tabla_usuarios = os.environ["TABLE_NAME_USUARIOS"]

        # Verificar la existencia del email y passsword
        if tenant_id and user_id and nombre and apell_pat and apell_mat and email and password:
            
            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)
            
            # Conectar DynamoDB
            dynamodb = boto3.resource('dynamodb')
            tp_usuarios = dynamodb.Table(tabla_usuarios)

            # Almacena los datos del use en la tabla de usuarios en el dynamoSSB
            tp_usuarios.put_item(
                Item = {
                    'tenant_id': tenant_id,
                    'user_id': user_id,
                    'email': email,
                    'nombre': nombre,
                    'apell_pat': apell_pat,
                    'apell_mat': apell_mat,
                    'password': hashed_password,
                    'rol': rol
                }
            )

            #Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': f'User {nombre} registered succesfully',
                'tenant_id': tenant_id,
                'user_id': user_id
            }

            return {
                'statusCode': 200,
                'body': mensaje
            }
        
        else:
            mensaje = {
                'error': 'Tiene datos pendientes'
            }

            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception: ", str(e))
        mensaje = {
            'error': str(e)
        }

        return {
            'statusCode': 500,
            'body': mensaje
        }
