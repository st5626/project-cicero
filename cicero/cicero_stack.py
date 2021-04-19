from aws_cdk import (
    core as cdk,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as _iam,
    aws_s3_notifications,
    aws_s3_deployment as s3_deployment,
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
        )
        transcribe_bucket = s3.Bucket(
            self,
            "TranscribeBucket",
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Initial Video Upload and Transcription
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

        # create s3 notification for lambda function
        notification = aws_s3_notifications.LambdaDestination(transcribe_lambda)

        # assign notification for the s3 event type
        video_upload_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, notification
        )
