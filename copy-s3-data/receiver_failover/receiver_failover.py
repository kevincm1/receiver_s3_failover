import json
import os
import boto3
import re

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

def get_object_key(event):
    return event["Records"][0]["s3"]["object"]["key"]

def get_object_bucket(event):
    return event["Records"][0]["s3"]["bucket"]["name"]

def get_sns_topic_arn():
    return os.getenv("SNS_TOPIC_ARN")

def get_provider(event):
    key = get_object_key(event)
    match = re.search(r"\d{4}-\d{2}-\d{2}\/(.*)-(\d{13}).zip", key)
    if match is None:
        return ""
    return match.group(1).lower()

def get_providers():
    providers = os.getenv("PROVIDERS_TO_PROCESS").replace(" ", "")
    providers = list(providers.split(","))
    return [provider.lower() for provider in providers]

def get_object_arn(event):
    key = get_object_key(event)
    bucket = get_object_bucket(event)
    return f"s3://{bucket}/{key}"

def should_process_this_event(event):
    providers = get_providers()
    if len(providers) == 0:
        print("PROVIDERS_TO_PROCESS is empty")
        return False
    provider = get_provider(event)
    return provider in providers

def lambda_handler(event, context):
    if should_process_this_event(event) is not True:
        print(f"Skipping provider {get_provider(event)}")
        return

    provider = get_provider(event)
    topic_arn = get_sns_topic_arn()
    message = get_object_arn(event)

    print(f"Publishing to SNS. ARN: {topic_arn}; Provider: {provider}; Message: {message}")
    try:
        response = sns_client.publish(
            TargetArn=topic_arn,
            Message=message,
            MessageStructure='string',
            MessageAttributes={
                'provider': {
                    'DataType': 'String',
                    'StringValue': provider,
                }
            }
        )
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        status = "Success" if status_code >= 200 and status_code < 300 else  "Fail"
        print(f"Publish to sns complete. Status: {status}; Provider: {provider}")
    except Exception as e:
        print(f"Publish to sns complete. Status: Fail; Message: {e}")