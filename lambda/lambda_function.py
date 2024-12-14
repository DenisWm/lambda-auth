import boto3
import json
import os

def lambda_handler(event, context):
    """Função principal que será invocada pela AWS Lambda"""
    cpf = event.get('cpf')

    if not cpf:
        return {
            'statusCode': 400,
            'body': json.dumps('CPF não fornecido.')
        }

    client = boto3.client(
        'cognito-idp', 
        aws_access_key_id='test', 
        aws_secret_access_key='test', 
        region_name='us-east-1', 
        endpoint_url='http://localhost:4566'
    )

    try:
        response = client.list_users(
            UserPoolId=os.environ.get('USER_POOL_ID'), 
            Filter=f'username = "{cpf}"'
        )

        if response['Users']:
            return {
                'statusCode': 200,
                'body': json.dumps(f'Usuário com CPF {cpf} foi encontrado.')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps(f'Usuário com CPF {cpf} não foi encontrado.')
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Ocorreu um erro: {str(e)}')
        }
