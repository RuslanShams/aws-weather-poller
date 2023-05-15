import boto3
import os
from dotenv import load_dotenv
from get_weather_class import GetWeather


def get_queue_url(client, id):
    response = client.get_queue_url(
        QueueName='weather_queue',
        QueueOwnerAWSAccountId=id
    )
    return response

def check_queue(client, queue_url):

    response = client.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    message = response.get('Messages', [{'Body': None}])[0]
    receipt_handle = message.get('ReceiptHandle', None)
    return message['Body'], receipt_handle

def delete_message(client, queue_url, receipt_handle):
    client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )

def get_weather_service(message):
    weather_service = GetWeather(message)
    weather_res = weather_service.get_weather()
    return weather_res

def lambda_handler(event, context):
    if not load_dotenv('make.env'):
        return 'make.env file upload error'

    id = os.environ['AWS_ACCOUNT_ID']
    client = boto3.client('sqs')
    queue_url = get_queue_url(client, id)['QueueUrl']
    message, receipt_handle = check_queue(client, queue_url)
    if message:
        weather_res = get_weather_service(message)
        delete_message(client, queue_url, receipt_handle)
        return weather_res
    else:
        return {"statusCode": 404}

