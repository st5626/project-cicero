import boto3
import time
import requests
import uuid
import os

def main(event, context):
    transcribe = boto3.client('transcribe')
    s3 = boto3.resource('s3')
    
    # Get uploaded video url
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    job_uri = f"s3://{bucket}/{key}"
    # job_name = f"Video_Transcribe_Job_{uuid.uuid4()}"
    job_name = str(uuid.uuid4())
    output_bucket = os.getenv('BUCKET')

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        OutputBucketName=output_bucket,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )

