import aws_cdk
from aws_cdk import App
from cdk.api_cores_lambda_stack import ApiCoresLambdaStack

app = App()
env = aws_cdk.Environment(region="us-east-1")
ApiCoresLambdaStack(app, "ApiCoresLambdaStack", env=env)
app.synth()
