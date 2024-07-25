# S3 Directory Upload Script

This Python script uploads a local directory to an Amazon S3 bucket.

## Dependencies

- Python 3
- Boto3
- AWS CLI

Before running the script, make sure that AWS CLI is configured with the correct access and secret keys. You can do this by running `aws configure` and following the prompts.

## Usage

The script takes three string parameters:

1. `bucket_name`: The name of the S3 bucket.
2. `directory`: The local directory to upload.
3. `directory_key`: The key for the directory in the S3 bucket. This is the name of the directory that will be created inside the bucket.

You can run the script from the command line like this:

```bash
python main.py <bucket_name> <directory> <directory_key>
```
Replace `<bucket_name>`, `<directory>`, and `<directory_key>` with your actual values.

## Example

Here's an example of how to use the script:

```bash
python main.py 'my-bucket' '/path/to/my/directory' 'my-directory'
```

This command will upload the contents of `/path/to/my/directory` to a new directory named `my-directory` in the `my-bucket` S3 bucket.