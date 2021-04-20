import boto3
import json
import os

def main(event, context):
    translate = boto3.cleint('translate')
    s3 = boto3.resource('s3')

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['bucket']['key']
    
    content_object = s3.Object(bucket, key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    textToSynthesize = json_content['results']['transcripts'][0]['transcript']
    output_bucket = os.getenv('OUTPUT_BUCKET')

    result = translate.translate_text(
        Text=textToSynthesize,
        SourceLanguageCode="en", 
        TargetLanguageCode="de",
        OutputBucketName=output_bucket,
        )