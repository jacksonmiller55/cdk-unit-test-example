import os.path
from os import path

from constructs import Construct
from aws_cdk import Stack, aws_lambda as _lambda, aws_apigateway as _apigw, aws_dynamodb


class ApiCoresLambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        table = aws_dynamodb.Table(
            self,
            "Example-DynamoDbTable",
            partition_key=aws_dynamodb.Attribute(
                name="first_name", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="last_name", type=aws_dynamodb.AttributeType.STRING
            ),
        )

        dirname = os.path.dirname(__file__)
        the_path = path.join(dirname, "../lambdaCode")

        function = _lambda.Function(
            self,
            "Example-ApiCoresLambda",
            handler="lambda_handler.handler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(path=the_path),
        )

        # Adding IAM
        table.grant_read_write_data(function)

        # TODO add environment variables
        function.add_environment("TABLE_NAME", table.table_name)

        api = _apigw.LambdaRestApi(
            self,
            "Example-ApGatewayWithCores",
            handler=function,
            rest_api_name="Example-ApGatewayWithCores",
        )

        rsvp_entity = api.root.add_resource(
            "rsvp",
            default_cors_preflight_options=_apigw.CorsOptions(
                allow_methods=["Post", "Options"], allow_origins=_apigw.Cors.ALL_ORIGINS
            ),
        )

        rsvp_entity_lambda_integration = _apigw.LambdaIntegration(
            function,
            proxy=True,
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseParamters": {
                        "meathod.response.reader.Access-Control-Allow-Origin": "*"
                    },
                }
            ],
        )

        rsvp_entity.add_method(
            "POST",
            rsvp_entity_lambda_integration,
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                }
            ],
        )
