import boto3
from botocore.exceptions import ClientError

# TODO: write some docs for each function

class S3:

    def __init__(self,bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def create(self):
        response = self.s3.list_buckets()
        # We have to extract the 'Buckets' object, which contains objects for each bucket.
        for bucket in response['Buckets']:
            if self.bucket_name == bucket['Name']:
                raise ValueError("A bucket named '{}' already exists under your current AWS account.".format(self.bucket_name))
            else:
                try:
                    response = self.s3.create_bucket(Bucket=self.bucket_name,
                            # TODO: Need to figure out how to make the region configurable.
                            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'},)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'BucketAlreadyExists':
                        raise ValueError("Failed to create bucket '{}': already exists under separate AWS account. Try a different bucket name.".format(self.bucket_name))
                    else:
                        print(e)
    
    def write_model(self,model,model_name):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name,Key=model_name)
            raise ValueError("A model with the specified name already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                #This is a good sign: it means the model hasn't been pushed to S3 yet.
                self.s3.put_object(Bucket=self.bucket_name,Key=model_name,Body=model)

