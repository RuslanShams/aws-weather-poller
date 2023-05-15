import boto3
import os
from dotenv import load_dotenv


class SQSProcessor:
    def __init__(self, name_queue='weather_queue'):
        if not load_dotenv('make.env'):
            print('make.env file upload error')
            return None

        self.session = boto3.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
                                     aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                     region_name=os.environ['REGION_NAME'])

        print(self.session)

        sqs_resource = boto3.resource('sqs')
        self.queue = sqs_resource.create_queue(QueueName=name_queue, Attributes={'DelaySeconds': '1'})
        self.sqs = boto3.client('sqs')

        print(self.queue.url)

    def send_message(self, message_body):
        self.sqs.send_message(
            QueueUrl=self.queue.url,
            MessageBody=message_body
        )

    def receive_and_delete(self):

        queue_url = self.queue.url

        response = self.sqs.receive_message(
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

        if receipt_handle:
            self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
        return message['Body']



