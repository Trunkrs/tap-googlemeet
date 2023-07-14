import json
import logging

import boto3

def get_secret(secret_id):
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId=secret_id)
    return json.loads(secret['SecretString'])


def update_secret(
        credentials,
        secret_id
):
    client = boto3.client('secretsmanager')
    value = json.dumps({
        'token': credentials['token'],
        'refresh_token': credentials['refresh_token'],
        'token_uri': credentials['token_uri'],
        'client_id': credentials['client_id'],
        'client_secret': credentials['client_secret'],
        'scopes': credentials['scopes'],
        'expiry': credentials['expiry'],
    })
    client.update_secret(
        SecretId=secret_id,
        SecretString=value,
    )