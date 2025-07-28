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
import os

class CdkStoriStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC for ECS services
        vpc = ec2.Vpc(self, "RagStoriVPC", max_azs=2)

        # ECS Cluster
        cluster = ecs.Cluster(self, "RagStoriCluster", vpc=vpc)

        # S3 Bucket for embeddings or storage
        bucket = s3.Bucket(self, "RagStoriDataBucket", versioned=True)

        # IAM Role for ECS tasks
        task_role = iam.Role(self, "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        # Grant S3 access to ECS task
        bucket.grant_read_write(task_role)

        # CloudWatch Logs group
        log_group = logs.LogGroup(self, "RagStoriLogGroup")

        # BACKEND SERVICE
        backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "BackendService",
            cluster=cluster,
            cpu=512,
            desired_count=1,
            memory_limit_mib=1024,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(os.path.join("..", "backend")),
                container_port=8000,
                task_role=task_role,
                log_driver=ecs.LogDriver.aws_logs(
                    stream_prefix="Backend",
                    log_group=log_group
                )
            ),
            public_load_balancer=True
        )

        # FRONTEND SERVICE
        frontend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FrontendService",
            cluster=cluster,
            cpu=256,
            desired_count=1,
            memory_limit_mib=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(os.path.join("..", "frontend")),
                container_port=80,
                task_role=task_role,
                log_driver=ecs.LogDriver.aws_logs(
                    stream_prefix="Frontend",
                    log_group=log_group
                )
            ),
            public_load_balancer=True
        )
