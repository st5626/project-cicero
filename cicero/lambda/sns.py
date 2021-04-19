import boto3
import os
from botocore.exceptions import ClientError

def main(event, context):
    ses = boto3.client('ses')
    s3 = boto3.resource('s3')
    
    # Get uploaded video url
    record = event['Records'][0]
    bucket_name = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    user_email = os.getenv('USER_EMAIL')

    content_object = s3.Object(bucket_name, key)

    # location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']
    url = "https://s3.amazonaws.com/%s/%s" % (bucket_name, key)

    
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = os.getenv('SENDER')
    
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = os.getenv('RECIEVER')

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    SUBJECT = "Cicero Video Processing Complete!"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Cicero Video Processing Complete!\r\n"
                f"Your Video is available at {url} "
                )
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>Cicero Video Processing Complete!</h1>
    <p>Your Video is available at
        <a href='{url}'>this link</a>.</p>
    </body>
    </html>
    """            
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])



