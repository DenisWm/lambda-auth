import boto3
import os

cognito = boto3.client('cognito-idp')

def handler(event, context):

    username = event.get('username')
    
    if not username:
        return {"statusCode": 400, "body": "CPF é obrigatório."}

    try:

        response = cognito.list_users(
            UserPoolId=os.environ['USER_POOL_ID'],
            Filter=f'username = "{username}"'
        )
        
        users = response.get('Users', [])
        if not users:
            return {"statusCode": 404, "body": "Usuário não encontrado."}

        user_info = users[0]
        return {
            "statusCode": 200,
            "body": {
                "username": user_info["Username"],
                "attributes": user_info["Attributes"]
            }
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
