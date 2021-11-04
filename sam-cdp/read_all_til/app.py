import json
from pymongo import MongoClient
import boto3


def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="ap-northeast-2"
    )
    get_secret_value_response = client.get_secret_value(
        SecretId='rds-secret-01'
    )
    token = get_secret_value_response['SecretString']
    return eval(token)


def db_ops():
    secrets = get_secret()
    client = MongoClient("mongodb://{0}:{1}@{2}".format(secrets['user'], secrets['password'], secrets['host']))
    return client


def lambda_handler(event, context):

    client = db_ops()
    db = client.dbStock
    idx = event['queryStringParameters']['idx']
    article = db.article.find_one({'idx': int(idx)}, {'_id': False, 'reg_date':False})

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        "body": json.dumps({
            "result": "success",
            "article": article
        }),
    }


