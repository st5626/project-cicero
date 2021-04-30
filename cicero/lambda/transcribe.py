import boto3
import time
import requests
import os
import logging

def main(event, context):
    transcribe = boto3.client('transcribe')
    s3 = boto3.resource('s3')
    dynamodb = boto3.resource("dynamodb")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Get uploaded video url
    logger.info(event)
    record = event['Records'][0]

    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    logger.info(key)
    job_uri = f"s3://{bucket}/{key}"
    output_bucket = os.getenv('BUCKET')
    table_name = os.getenv("TABLE")
    table = dynamodb.Table(table_name)
    table_record = table.get_item(
        Key={
            'uuid': key,
        }
    )
    
    input_language = table_record['Item']["input_language"]
    transcribe.start_transcription_job(
        TranscriptionJobName=key,
        OutputBucketName=output_bucket,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp4',
        LanguageCode=input_language,
    )

