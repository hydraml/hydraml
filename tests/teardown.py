import boto3
from botocore.exceptions import ClientError
'''
Helper class to tear down AWS resources to save cost and avoid clutter.
Todo:
    * Add single bucket teardown 
    * Modify write_model() to input data blob instead of file
'''
class Teardown:

    def __init__(self):
        '''
        The name of the bucket must be passed into the S3 constructor.
        Constructor will then instantiate the boto3 client and retrieve
        the region name using the boto3.session.Session class
        '''
        self.s3 = boto3.client('s3')
        self.region = boto3.session.Session().region_name
    
    def s3_teardown_all(self):
        buckets = self.s3.list_buckets()['Buckets']
        if not buckets:
            print ("No buckets to delete in region '{}'".format(self.region)) 
        for bucket in buckets:
            bucket_name = bucket['Name']
            # Must first delete all objects in bucket before deleting bucket
            boto3.resource('s3').Bucket(bucket_name).objects.all().delete()
            response = self.s3.delete_bucket(Bucket=bucket_name)
            print ("Bucket '{}' deleted.".format(bucket_name))
