import boto3, uuid
from botocore.exceptions import ClientError
'''
Wrapper class for working with AWS APIGateway. Abstracts details of
boto3 package for the manager class.
Todo:
    * Example todo
    * Modify write_model() to input data blob instead of file
'''
class APIGateway:

    def __init__(self):
        '''
        Constructor will then instantiate the boto3 client and retrieve
        the region name using the boto3.session.Session class
        '''
        self.api = boto3.client('apigateway')
        self.aws_lambda = boto3.client('lambda')
        self.lambda_version = self.aws_lambda.meta.service_model.api_version
        self.region = boto3.session.Session().region_name
        self.account_id = boto3.client('sts').get_caller_identity()['Account']

    def create_gateway(self, function_name, api_name):
        '''
        Credit for most of the function code goes to GitHub user AJRenold:
        https://github.com/boto/boto3/issues/572#issuecomment-209693915
        '''
        # Create API and grab API ID + root resource ID
        lambda_api_id = self.api.create_rest_api(name=api_name,
                endpointConfiguration={
                    'types': ['REGIONAL']
                })['id']
        root_resource_id = self.api.get_resources(restApiId=lambda_api_id)['items'][0]['id']

        ## create resource
        response = self.api.create_resource(
            restApiId=lambda_api_id,
            parentId=root_resource_id, # resource id for the Base API path
            pathPart=function_name)

        ## create POST method
        put_method_resp = self.api.put_method(
            restApiId=lambda_api_id,
            resourceId=response['id'],
            httpMethod="POST",
            authorizationType="NONE",
            apiKeyRequired=True,)

        uri_data = {
        "aws-api-id": lambda_api_id,
        "aws-region": self.region,
        "api-version": self.lambda_version,
        "aws-acct-id": self.account_id,
        "lambda-function-name": function_name,}

        uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(**uri_data)

        ## create integration
        integration_resp = self.api.put_integration(
            restApiId=lambda_api_id,
            resourceId=response['id'],
            httpMethod="POST",
            type="AWS",
            integrationHttpMethod="POST",
            uri=uri,)

        self.api.put_integration_response(
            restApiId=lambda_api_id,
            resourceId=response['id'],
            httpMethod="POST",
            statusCode="200",
            selectionPattern=".*")

        ## create POST method response
        self.api.put_method_response(
            restApiId=lambda_api_id,
            resourceId=response['id'],
            httpMethod="POST",
            statusCode="200",)

        source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/POST/{lambda-function-name}".format(**uri_data)

        self.aws_lambda.add_permission(
            FunctionName=function_name,
            StatementId=uuid.uuid4().hex,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn)

        # state 'your stage name' was already created via API Gateway GUI
        self.api.create_deployment(
            restApiId=lambda_api_id,
            stageName='stage')

    def delete_gateway(self, api_name):
        rest_apis = self.api.get_rest_apis()['items']
        for rest_api in rest_apis:
            if rest_api['name'] == api_name:
                self.api.delete_rest_api(restApiId=rest_api['id'])
                print("API Gateway '{}' deleted.".format(rest_api['name']))


