from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_logs as logs
)
from constructs import Construct

class RagStoriStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC - all ECS services and networking will be within the VPC
        vpc = ec2.Vpc(self, "RagStoriVPC", max_azs=2)

        # ECS Cluster for orchestrating the Fargate containers
        cluster = ecs.Cluster(self, "RagStoriCluster", vpc=vpc)

        # S3 Bucket for storing embeddings, documents, or logging if needed
        bucket = s3.Bucket(self, "RagStoriDataBucket", versioned=True)

        # IAM Role for ECS tasks
        task_role = iam.Role(self, "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        # Grant access to the S3 bucket for the ECS task
        bucket.grant_read_write(task_role)

        # Log group for storing container logs in CloudWatch
        log_group = logs.LogGroup(self, "RagStoriLogGroup")

        # Fargate Service (frontend and backend served in a single container for now)
        ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "RagStoriService",
            cluster=cluster,
            cpu=512,
            desired_count=1,
            memory_limit_mib=1024,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("../"),
                container_port=80,
                task_role=task_role,
                log_driver=ecs.LogDriver.aws_logs(
                    stream_prefix="RagStoriApp",
                    log_group=log_group
                )
            )
        )
