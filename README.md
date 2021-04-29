# Project Cicero

## Local Setup

1. Ensure NodeJS is installed as well as Docker and the AWS CDK toolkit is set up [correctly](https://docs.aws.amazon.com/cdk/latest/guide/work-with.html#work-with-prerequisites). To get your AWS credentials with your educate account click the account details button before signing in and copy and paste the CLI details into the .aws folder.
   ![](https://user-images.githubusercontent.com/31460379/112003536-5d314f80-8af7-11eb-8912-1a53db51ce73.png)
    `> vim ~/.aws/credentials`
2. Make sure Python 3.6 or higher is [installed](https://www.python.org/downloads/) along with pip and virtualenv packages.
3. Source virtual environment for Python packages.

    `> source .venv/bin/activate`
4. Install packages.

    `> pip install -r requirements.txt`

5. [Verify an email to use for SNS service](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html)
   You can also verify email using boto3
   ```
   def verify_email_identity():
    ses_client = boto3.client("ses", region_name="us-east-2")
    response = ses_client.verify_email_identity(
        EmailAddress="abc1234@rit.edu"
    )
    print(response)
    ```
    This MUST be done for the sender email. The recipient email must also be verified if you are using SES in sandbox mode.
    Note: SES does not work on AWS Educate. Use a regular or free tier.

6. Profit

For more information on how to add modules and documentation on modules check out the AWS [docs](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html). Make sure any new modules are added to `requirements.txt` with correct versioning.


## Language Codes

`arb | cmn-CN | cy-GB | da-DK | de-DE | en-AU | en-GB | en-GB-WLS | en-IN | en-US | es-ES | es-MX | es-US | fr-CA | fr-FR | is-IS | it-IT | ja-JP | hi-IN | ko-KR | nb-NO | nl-NL | pl-PL | pt-BR | pt-PT | ro-RO | ru-RU | sv-SE | tr-TR`

## Synthesize and Deploy
Stacks can be simply synthesized into Cloudformation templates or directly deployed from the command line.

### Bootstrap (do this first)
`> cdk bootstrap`

### Synthesize
`> cdk synth`

### Deploy
`> cdk deploy`

### Destroy
`> cdk destroy`

## Actually using it

1. Deploy the stack using the steps above.

2. Find the location of the static site's S3 URL. When the bucket is made it is automatically public and available for static usage.

3. Once on the website fill in the required information. This includes the API URL from the gateway. This was necessary due to the order in which the resources are created. The URL was not known at the time of creating the static site. The language codes can be found in a section above. As a disclaimer we have run into some transient issues with large video files. So if that is an issue try with a smaller video.

4. Once submitted the video should begin processing. You may look at the individual buckets to see the flow of data. Once the video is finished it is placed in the finished video bucket. If your email address was verified you should also receive an email with a link to your finished video.
