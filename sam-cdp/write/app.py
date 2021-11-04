import json
from pymongo import MongoClient
import boto3
import datetime


def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="ap-northeast-2"
    )
    get_secret_value_response = client.get_secret_value(
        SecretId='cdp-secret-01'
    )
    token = get_secret_value_response['SecretString']
    return eval(token)


def db_ops():
    secrets = get_secret()
    client = MongoClient("mongodb://{0}:{1}@{2}".format(secrets['user'], secrets['password'], secrets['host']))
    return client


def lambda_handler(event, context):
    client = db_ops()
    db = client.tdp

    body = json.loads(event['body'])
    til_title_receive = body['til_title_give']
    til_content_receive = body['til_content_give']
    til_count = db.til.count()
    if til_count == 0:
        max_value = 1
    else:
        max_value = db.til.find_one(sort=[("til_idx", -1)])['til_idx'] + 1

    doc = {'til_idx': max_value, 'til_title': til_title_receive,
           'til_content': til_content_receive, 'til_day': datetime.datetime.now(), 'til_view': True}
    db.til.insert_one(doc)

    return{
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        "body": json.dumps({'msg': 'til 작성 완료!'})
    }

