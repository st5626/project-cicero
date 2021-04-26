import boto3
import os
import json
import uuid

dynamodb = boto3.resource("dynamodb")

def main(event, context):
    _json = json.loads(event["body"])
    filename = _json["filename"]
    input_lang = _json["input_language"]
    target_lang = _json["target_language"]
    email = _json["email"]
    bucket = os.getenv("BUCKET")
    table_name = os.getenv("TABLE")
    table = dynamodb.Table(table_name)
    key = str(uuid.uuid4())
    url = boto3.client("s3").generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600,
    )

    table.put_item(Item={
        "uuid": key,
        "filename": filename, 
        "input_language": input_lang,
        "target_language": target_lang,
        "email": email,
        }
    )

    return {
        "statusCode": 200,
        "body": url,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
    }
