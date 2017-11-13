import boto3
import os

from .s3 import S3


class AWSLambda:

    def __init__(self, project_name, bucket_name=None, function_name=None, runtime="python3.6"):
        self.project_name = "{}-lambda".format(project_name)
        self.bucket_name = bucket_name
        self.function_name = function_name
        self.runtime = runtime
        self.client = boto3.client('lambda')
        self.function_path = os.path.abspath(os.path.join(
                                                     os.path.dirname( __file__ ),
                                                     '..',
                                                     'function.zip'
                                                     )
                                        )

        if self.bucket_name:
            self.s3 = S3(self.bucket_name)
        else:
            self.s3 = None

    def deploy_function(self, model_bucket_name, model_name, role=None):
        self.client.create_function(
            FunctionName=self.project_name,
            Runtime=self.runtime,
            Role=self.role,
            Handler='handler.predict',
            Code={'ZipFile': open(self.function_path)},
            Description='Lambda Function serving a machine learning model as an API',
            Publish=True,
            Environment={
                'bucket_name': model_bucket_name,
                'model_name': model_name
            },
        )

    def set_role(self):
        self.role = None

    def destroy_function(self):
        self.client.delete_function(FunctionName=self.project_name)

    def validate_function_name(self):
        return self.function_name.endswith('.zip')

    def soft_deploy_function(self):
        if not self.s3:
            raise NameError("Deploy Bucket does not exist")

        if not self.bucket_name or not self.function_name:
            raise AttributeError("bucket_name and function_name must be defined for soft deploy")

        if not self.validate_function_name():
            raise NameError("function_name must end in .zip")

        function_data = open(self.function_path)
        self.s3.upload_function(function_data, self.function_name)
