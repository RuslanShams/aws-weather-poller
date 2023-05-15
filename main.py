import schedule
import boto3
import requests
import json
from threading import Thread
from create_queue import SQSProcessor


def find_lambda_function(function_name):
    client = boto3.client('lambda')
    list_functions_resp = client.list_functions()
    for element in list_functions_resp['Functions']:
        if function_name in element['FunctionName']:
            return element['FunctionName']
    raise Exception('Function not found')


def create_lambda_url_config(function_name):
    client = boto3.client('lambda')
    try:
        response = client.create_function_url_config(
            FunctionName=function_name,
            AuthType='NONE'
        )
    except:
        response = client.get_function_url_config(
            FunctionName=function_name,
        )
    return response['FunctionUrl']


def fill_queue(queue):
    while True:
        message = input('Enter the city name or type \'stop\':')
        if message == 'stop':
            break
        queue.send_message(message)


def get_weather_from_lambda(lambda_function_url):
    res = requests.get(lambda_function_url)
    if res.status_code == 200:
        try:
            dic = eval(res.content.decode('utf-8'))
            with open("weather.json", "a+") as outfile:
                json.dump(dic, outfile, indent=2)
        except Exception as er:
            print("Exception (weather):", er)


def lamb_schedule(lambda_function_url):
    schedule.every(10).seconds.do(get_weather_from_lambda, lambda_function_url)
    while True:
        schedule.run_pending()


def main():
    function_name = find_lambda_function('MyLambdaFunction')
    lambda_function_url = create_lambda_url_config(function_name)
    queue = SQSProcessor()
    fill_queue_thread = Thread(target=fill_queue, args=(queue,))
    lamb_schedule_thread = Thread(target=lamb_schedule, args=(lambda_function_url,))
    fill_queue_thread.start()
    lamb_schedule_thread.start()
    fill_queue_thread.join()
    lamb_schedule_thread.join()


if __name__ == '__main__':
    main()
