import boto3
import OutputS3BucketName

def main(event, context):
    translate = boto3.cleint('translate')
    s3 = boto3.resource('s3')

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['bucket']['key']
    