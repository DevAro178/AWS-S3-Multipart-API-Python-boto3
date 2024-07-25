import boto3, os, sys, threading, time, botocore, argparse
from boto3.s3.transfer import TransferConfig
s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')
#  ---------------------- ---------------------- Basic Commands ---------------------- ----------------------  #

# # Creating a bucket 
# s3_resource.create_bucket(Bucket="lms-gb-attachments-bucket-multipart-upload-api",CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'})

# # listing all buckets
# for bucket in s3_resource.buckets.all():
#     print(bucket.name)

# # Uploading a file to S3
# s3_resource.Object('lms-gb-attachments-bucket', '.env').upload_file(Filename='.env')

# # Print objects in a specific bucket
# for obj in s3_resource.Bucket ('lms-gb-attachments-bucket').objects.all():
#     print(obj.key)

# # Delete an object
# s3_resource.Object('lms-gb-attachments-bucket', '.env').delete()

#  ---------------------- ---------------------- Data Upload using Multi Part ---------------------- ----------------------  #
# Create the parser
parser = argparse.ArgumentParser(description="This script uploads a directory to an S3 bucket.")

# Add the arguments
parser.add_argument('bucket_name', metavar='bucket', type=str, help='The name of the S3 bucket.')
parser.add_argument('directory', metavar='directory path', type=str, help='The local directory to upload.')
parser.add_argument('directory_key', metavar='key', type=str, help='The key for the directory in the S3 bucket.')

# Parse the arguments
args = parser.parse_args()

bucket_name = args.bucket_name
directory = args.directory
directory_key = args.directory_key

config = TransferConfig(multipart_threshold=1024 * 25, 
                        max_concurrency=20,
                        multipart_chunksize=1024 * 50,
                        use_threads=True)

def multipart_upload_boto3(bucket_name, key, file_path):

    class ProgressPercentage(object):
        def __init__(self, filename):
            self._filename = filename
            self._size = float(os.path.getsize(filename))
            self._seen_so_far = 0
            self._lock = threading.Lock()
            self._start_time = time.time()

        def __call__(self, bytes_amount):
            with self._lock:
                self._seen_so_far += bytes_amount
                percentage = (self._seen_so_far / self._size) * 100
                elapsed_time = time.time() - self._start_time
                speed = self._seen_so_far / elapsed_time / 1024 / 1024  # Speed in MB/s
                sys.stdout.write(
                    "\r%s  %s / %s  (%.2f%%)  Speed: %.2f MB/s" % (
                        self._filename, self._seen_so_far, self._size,
                        percentage, speed))
                sys.stdout.flush()

    s3_resource.Object(bucket_name, key).upload_file(file_path,
                            Config=config,
                            Callback=ProgressPercentage(file_path)
                            )
    

class upload_directories():
    def __init__(self, bucket_name, directory,directory_key,updateCheck=False):
        """
        bucket_name: The name of the S3 bucket.
        directory: The local directory to upload.
        directory_key: The key for the directory in the S3 bucket.
        updateCheck: Whether to check if files are already present in the S3 bucket before uploading. Defaults to False.
        """
        
        # get the file count
        self.file_count = 0
        self.uploaded_files_count = 0
        for root, dirs, files in os.walk(directory):
            self.file_count += len(files)
            
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                key = file_path.replace(directory, directory_key).replace('\\', '/').lstrip('/')
                if not updateCheck:
                    multipart_upload_boto3(bucket_name, key, file_path)
                    self.update_uploaded_files_count(1)
                else:
                    try:
                        s3_client.head_object(Bucket=bucket_name, Key=key)
                        print(f"{key} already exists in {bucket_name}.")
                        self.update_uploaded_files_count(1)
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            multipart_upload_boto3(bucket_name, key, file_path)
                            print(f"{key} uploaded to {bucket_name}.")
                            self.update_uploaded_files_count(1)
                        
    def update_uploaded_files_count(self,increment):
        self.uploaded_files_count+=increment
        print('--------------------')
        print(f'{self.uploaded_files_count}/{self.file_count} files uploaded. - - - Percentage: {round((self.uploaded_files_count/self.file_count)*100, 2)}%')
        print('--------------------')
        

upload_directories(bucket_name, directory,directory_key,True)