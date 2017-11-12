import sklearn as sk

from .s3 import S3
from .aws_lambda import AWSLambda


class Manager:

    def __init__(self, project_name, model_name, deploy_bucket=None, function_name=None, runtime="python3.6"):
        self.project_name = project_name
        self.model_name = model_name # add file extenstion!
        self.deploy_bucket = deploy_bucket
        self.function_name = function_name
        self.runtime = runtime
        self.s3 = S3(self.project_name) #provide existing s3?
        self.aws_lambda = AWSLambda(self.project_name, self.deploy_bucket, self.function_name, self.runtime) # provide existing lambda?

    def serialize_model(self, model):
        pass

    def validate_project_name(self):
        pass

    def deploy(self, model):
        # need APIGateway
        # Return service class?
        self.s3.create_if_not_exists()
        self.s3.upload_model(model, self.model_name)
        self.aws_lambda.deploy_function(self.s3.get_bucket_name(), self.model_name)

    def refresh(self, model):
        self.s3.upload_model(model, self.model_name)

    def soft_deploy(self, model):
        if not self.deploy_bucket or not self.function_name:
            raise AttributeError("deploy_bucket and function_name must be defined for soft deploy")

        self.s3.upload_model(model, self.model_name)
        self.aws_lambda.soft_deploy_function()

    def destroy(self):
        self.aws_lambda.destroy_function()
        self.s3.destroy()  # empty contents?
