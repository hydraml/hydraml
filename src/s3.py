import boto3
from botocore.exceptions import ClientError
'''
Wrapper class for working with AWS S3. Abstracts details of
boto3 package for the manager class.

Todo:
    * Example todo
    * Modify write_model() to input data blob instead of file

'''
class S3:

    def __init__(self,bucket_name):
        '''
        The name of the bucket must be passed into the S3 constructor.
        Constructor will then instantiate the boto3 client and retrieve
        the region name using the boto3.session.Session class
        '''
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
        self.region = boto3.session.Session().region_name

    def create_if_not_exists(self):
        '''
        Creates a bucket with the name passed into the constructor, if the
        bucket does not already exists. Fails if bucket is created within
        same AWS account or another AWS account
        '''
        response = self.s3.list_buckets()
        if self.bucket_name in map(lambda x: x['Name'], response['Buckets']):
            raise ValueError("A bucket named '{}' already exists under your current AWS account.".format(self.bucket_name))
        else:
            try:
                self.s3.create_bucket(Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region},)
                print ("Bucket '{}' created.".format(self.bucket_name))
            except ClientError as e:
                if e.response['Error']['Code'] == 'BucketAlreadyExists':
                    raise ValueError("Failed to create bucket '{}': already exists under separate AWS account. Try a different bucket name.".format(self.bucket_name))
                else:
                    print(e)
    
    def upload_model(self,model,model_name):
        '''
        Uploades a trained model to the S3 bucket, if a model with the
        specified name does not already exists.
        '''
        try:
            response = self.s3.get_object(Bucket=self.bucket_name,Key=model_name)
            raise ValueError("A model with the specified name already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                #This is a good sign: it means the model hasn't been pushed to S3 yet.
                self.s3.put_object(Bucket=self.bucket_name,Key=model_name,Body=model)

