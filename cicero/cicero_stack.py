from aws_cdk import (
    core as cdk,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as _iam,
    aws_s3_notifications,
    aws_s3_deployment as s3_deployment,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
)

class CiceroStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda role for using S3 buckets
        lambda_role = _iam.Role(
            scope=self,
            id="cdk-lambda-role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="cdk-lambda-role",
            managed_policies=[
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonTranscribeFullAccess"
                ),
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonPollyFullAccess"
                ),
                _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"),
            ],
        )

        # Static Website Creation
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            website_index_document="index.html",
            public_read_access=True,
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(
                restrict_public_buckets=False,
                ignore_public_acls=False,
                block_public_policy=False,
                block_public_acls=False,
            ),
        )

        api = apigateway.RestApi(
            self,
            "upload-api",
            rest_api_name="Cicero Service",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            ),
        )

        # Dynamo DB
        video_table = dynamodb.Table(
            self,
            "VideoTable",
            partition_key=dynamodb.Attribute(
                name="filename", type=dynamodb.AttributeType.STRING
            ),
        )

        s3_deployment.BucketDeployment(
            self,
            "DeployWebsite",
            destination_bucket=website_bucket,
            sources=[s3_deployment.Source.asset("./website")],
        )

        # create s3 bucket
        video_upload_bucket = s3.Bucket(
            self,
            "VideoUploadBucket",
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(
                restrict_public_buckets=False,
                ignore_public_acls=False,
                block_public_policy=False,
                block_public_acls=False,
            ),
            cors=[
                s3.CorsRule(
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    allowed_methods=[s3.HttpMethods.PUT],
                )
            ],
        )
        transcribe_bucket = s3.Bucket(
            self,
            "TranscribeBucket",
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        # translated_bucket = s3.Bucket(
        #     self,
        #     "TranslatedBucket",
        #     auto_delete_objects=True,
        #     removal_policy=cdk.RemovalPolicy.DESTROY,
        # )
        translated_audio_bucket = s3.Bucket(
            self,
            "TranslatedAudioBucket",
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Finished Video Bucket
        finished_video_bucket = s3.Bucket(
            self,
            "FinishedVideoBucket",
            auto_delete_objects=True,
            public_read_access=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        translated_text_bucket = s3.Bucket(
            self,
            "TranslateBucket",
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Initial Video Upload and Transcription
        video_upload_lambda = _lambda.Function(
            self,
            "video_upload_lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="video_upload.main",
            timeout=cdk.Duration.seconds(30),
            code=_lambda.Code.from_asset("./cicero/lambda"),
            role=lambda_role,
            environment={
                "BUCKET": video_upload_bucket.bucket_name,
                "TABLE": video_table.table_name,
            },
        )
        video_table.grant_write_data(video_upload_lambda)
        transcribe_lambda = _lambda.Function(
            self,
            "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="transcribe.main",
            timeout=cdk.Duration.seconds(30),
            code=_lambda.Code.from_asset("./cicero/lambda"),
            role=lambda_role,
            environment={"BUCKET": transcribe_bucket.bucket_name},
        )

        # Convert translated transcript to translated voice over
        polly_lambda = _lambda.Function(
            self,
            "polly_lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="polly.main",
            timeout=cdk.Duration.seconds(30),
            code=_lambda.Code.from_asset("./cicero/lambda"),
            role=lambda_role,
            environment={"OUTPUT_BUCKET": translated_audio_bucket.bucket_name},
        )

        # TODO: Email should be pulled from S3 bucket meta data? we will pull from the environment for now
        # Replace sender@example.com with your "From" address.
        # This address MUST be verified with Amazon SES.

        # Replace recipient@example.com with a "To" address. If your account
        # is still in the sandbox, this address must be verified.
        sns_lambda = _lambda.Function(
            self,
            "sns_lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="sns.main",
            timeout=cdk.Duration.seconds(30),
            code=_lambda.Code.from_asset("./cicero/lambda"),
            role=lambda_role,
            environment={
                "RECIEVER": "recipient@example.com",
                "SENDER": "Sender Name <sender@example.com>",
            },
        # Translate the transcribed text to the targeted language
        translate_lambda = _lambda.Function(
            self,
            "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler="translate.main",
            timeout=cdk.Duration.seconds(30),
            code=_lambda.Code.from_asset("./cicero/lambda"),
            role=lambda_role,
            environment={"OUTPUT_BUCKET": translated_text_bucket.bucket_name},
        )

        # create s3 notification for lambda function
        notification = aws_s3_notifications.LambdaDestination(transcribe_lambda)

        # create s3 notification for lambda function
        new_translation_notification = aws_s3_notifications.LambdaDestination(
            polly_lambda
        )
        finished_video_notification = aws_s3_notifications.LambdaDestination(sns_lambda)

        # API Gateway add route
        video_upload_integration = apigateway.LambdaIntegration(
            video_upload_lambda,
            request_templates={"application/json": '{ "statusCode": "200" }'},
        )
        api.root.add_method("POST", video_upload_integration)
        # assign notification for the s3 event type
        video_upload_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, notification
        )

        # TODO: Replace actual line with commented out line when actual transcripts are made
        # translated_bucket.add_event_notification(
        transcribe_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, new_translation_notification
        )

        finished_video_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, finished_video_notification
        )
