import boto3
import json
import os
import logging

def main(event, context):
    translate = boto3.client('translate')
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    content_object = s3.Object(bucket, key)
    logger.info(content_object)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    logger.info(file_content)
    json_content = json.loads(file_content)
    logger.info(json_content)
    textToSynthesize = json_content['results']['transcripts'][0]['transcript']
    job_name = json_content["jobName"]
    output_bucket = os.getenv('OUTPUT_BUCKET')
    result = translate.translate_text(
        Text=textToSynthesize,
        SourceLanguageCode="en", 
        TargetLanguageCode="de",
    )
    logger.info(result)
    output_json_name = job_name + ".json"
    s3object = s3.Object(output_bucket, output_json_name)
    s3object.put(
        Body=(bytes(json.dumps(result).encode('utf-8')))
    )