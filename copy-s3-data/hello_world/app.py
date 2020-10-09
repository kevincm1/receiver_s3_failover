import json
import os
import boto3

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

DEFAULT_REGION = "us-east-1"
DEFAULT_SNS_TOPIC = "kevin-test"

def get_object_key(event):
    return event["Records"][0]["s3"]["object"]["key"]

def get_object_bucket(event):
    return event["Records"][0]["s3"]["bucket"]["name"]

def get_object_destination(event):
    key = get_object_key(event)
    bucket = os.getenv("DESTINATION_BUCKET_NAME")
    return f"s3://{bucket}/{key}"

def get_sns_topic_arn():
    sns_topic_name = os.getenv("SNS_TOPIC", DEFAULT_SNS_TOPIC)
    aws_region = os.getenv("REGION", DEFAULT_REGION)
    aws_account_id = os.getenv("ACCOUNT_ID")
    topic_name = sns_topic_name
    return f"arn:aws:sns:{aws_region}:{aws_account_id}:{topic_name}"

def lambda_handler(event, context):
    # provider = get_provider()
    bucket = get_object_bucket(event)
    key = get_object_key(event)
    source = f"{bucket}/{key}"

    response = s3_client.copy_object(
        Bucket=os.getenv("DESTINATION_BUCKET_NAME"),
        CopySource=source,
        Key=key,
    )

    print(f"publish to s3 response: {response}")

    topic_arn = get_sns_topic_arn()
    message = get_object_destination(event)

    response = sns_client.publish(
        TargetArn=topic_arn,
        Message=message,
        MessageStructure='string',
        MessageAttributes={
            'provider': {
                'DataType': 'string',
                'StringValue': '',
            }
        }
    )

    print(f"publish to sns response: {response}")
