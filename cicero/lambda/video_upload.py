import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")

def main(event, context):
    _json = json.loads(event["body"])
    filename = _json["filename"]
    lang = _json["language"]
    email = _json["email"]
    bucket = os.getenv("BUCKET")
    table_name = os.getenv("TABLE")
    table = dynamodb.Table(table_name)

    url = boto3.client("s3").generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket, "Key": filename},
        ExpiresIn=3600,
    )

    table.put_item(Item={"filename": filename, "language": lang, "email": email})

    return {
        "statusCode": 200,
        "body": url,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
    }
