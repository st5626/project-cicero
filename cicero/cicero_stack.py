from aws_cdk import core as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3_deployment


class CiceroStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
