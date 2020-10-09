import json
import os
import boto3

client = boto3.client('s3')

def get_object_destination_path(event):
    key = get_object_key(event)
    path = os.path.dirname(key)
    bucket = os.getenv("DESTINATION_BUCKET_NAME")
    return "s3://" + bucket + "/" + path

def get_object_key(event):
    return event["Records"][0]["s3"]["object"]["key"]

def get_object_bucket(event):
    return event["Records"][0]["s3"]["bucket"]["name"]

def get_source_object_path(event):
    key = get_object_key(event)
    bucket = get_object_bucket(event)
    return "s3://" + bucket + "/" + key

def get_object(event):
    bucket = get_object_bucket(event)
    key = get_object_key(event)
    return client.get_object(Bucket=bucket, Key=key)

def put_object(object, event):
    bucket = get_object_bucket(event)
    key = get_object_key(event)
    print("key: ", key)
    print("bucket: ", bucket)
    print("object: ", object)
    # client.put_object(Body=object, Bucket=bucket, Key=key)


# dest = s3.Bucket('Bucketname2')
# dest.copy(source, 'backupfile')
def lambda_handler(event, context):
    # TODO: 
    # push notification to nmea-notifications SNS

    # comments?
    # raise exceptions?

    bucket = get_object_bucket(event)
    key = get_object_key(event)
    source = bucket + "/" + key
    response = client.copy_object(
        Bucket=os.getenv("DESTINATION_BUCKET_NAME"),
        CopySource=source,
        Key=key,
    )

    print(response)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
