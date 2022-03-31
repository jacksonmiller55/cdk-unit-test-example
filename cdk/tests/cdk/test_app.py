from cdk.app import ApiCoresLambdaStack
import aws_cdk as cdk
from aws_cdk.assertions import Template


def test_app_dynamodb_resource():
    app = cdk.App()
    processor_stack = ApiCoresLambdaStack(
        app,
        "ApiCorsLambdaStack",
    )

    template = Template.from_stack(processor_stack)
    dynamo_table = "AWS::DynamoDB::Table"
    dynamodb_properties = {
        "Type": "AWS::DynamoDB::Table",
        "Properties": {
            "KeySchema": [
                {"AttributeName": "first_name", "KeyType": "HASH"},
                {"AttributeName": "last_name", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "first_name", "AttributeType": "S"},
                {"AttributeName": "last_name", "AttributeType": "S"},
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        },
        "UpdateReplacePolicy": "Retain",
        "DeletionPolicy": "Retain",
    }
    template.has_resource(dynamo_table, props=dynamodb_properties)
