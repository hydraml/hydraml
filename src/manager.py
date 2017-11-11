import sklearn as sk

from .s3 import S3
from .aws_lambda import AWSLambda


class Manager:

    def __init__(self, project_name, model_name):
        self.project_name = project_name
        self.model_name = model_name
        self.s3 = S3(self.name) #provide existing s3?
        self.aws_lambda = AWSLambda(self.name) # provide existing lambda?

    def serialize_model(self, model):
        pass

    def deploy(self, model):
        # need APIGateway
        # Return service class?
        self.s3.create_if_not_exists()
        self.s3.upload_model(model, self.model_name)
        self.aws_lambda.deploy()

    def refresh(self, model):
        self.s3.upload_model(model, self.model_name)

    def soft_deploy(self, model):
        self.s3.upload_model(model, self.model_name)
        self.aws_lambda.soft_deploy()

    def destroy(self):
        self.aws_lambda.destroy()
        self.s3.destroy() # empty contents?
