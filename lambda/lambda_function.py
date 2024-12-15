import logging
import os
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('Iniciando a execução da Lambda...')
    logger.info(f'Evento recebido: {event}')

    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError as e:
        logger.error(f'Erro ao decodificar o body: {str(e)}')
        return {
            'statusCode': 400,
            'body': 'Formato do body inválido.'
        }

    cpf = body.get('cpf')

    if not cpf:
        logger.error('CPF não fornecido')
        return {
            'statusCode': 400,
            'body': 'CPF não fornecido.'
        }

    client = boto3.client(
        'cognito-idp', 
        aws_access_key_id='test', 
        aws_secret_access_key='test', 
        region_name='us-east-1', 
        endpoint_url='http://localstack:4566'
    )

    try:
        logger.info(f'Buscando usuário com CPF: {cpf}')
        response = client.list_users(
            UserPoolId=os.environ.get('USER_POOL_ID'), 
            Filter=f'username = "{cpf}"'
        )
        logger.info(f'Resposta do Cognito: {response}')
        
        if response['Users']:
            user = response['Users'][0]
            email = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'email'), 'Email não encontrado')

            logger.info(f'Usuário encontrado: CPF={cpf}, Email={email}')

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Usuário encontrado',
                    'cpf': cpf,
                    'email': email
                })
            }
        else:
            logger.info(f'Usuário com CPF {cpf} não foi encontrado.')
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'Usuário não encontrado',
                    'cpf': cpf
                })
            }
    except Exception as e:
        logger.error(f'Ocorreu um erro: {str(e)}')
        return {
            'statusCode': 500,
            'body': f'Ocorreu um erro: {str(e)}'
        }
