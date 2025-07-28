#!/usr/bin/env python3

import aws_cdk as cdk
from app_stack import RagStoriStack  

app = cdk.App()
RagStoriStack(app, "RagStoriStack")
app.synth()
