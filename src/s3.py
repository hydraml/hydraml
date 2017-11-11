import boto3
'''
TODO: 
    -Create bucket if it doesn't exist
    -Write model to bucket


'''
class S3:

    def __init__(self,bucket_name):
        self.s3 = boto3.client('s3')
        self.name = bucket_name

    
    def create():
        response = self.s3.list_buckets()
        if self.bucket_name in response['Buckets']:
            print("Bucket {} already exists".format(self.bucket_name))
        else:
            try:
                response = self.s3.create_bucket(Bucket=self.bucket_name)
            except ClientError:
                raise ValueError("Failed to create bucket. Try a different bucket name.")
    
    def write_model(self,model,model_name):
        response = self.s3.get_object(Bucket=self.bucket_name,Key=model_name)
        if response['Body']:
            raise ValueError("A model with the specified name already exists")
        else:
            self.s3.put_object(Bucket=self.bucket_name,Key=model_name,Body=model)
