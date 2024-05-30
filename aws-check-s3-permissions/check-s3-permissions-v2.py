import boto3
from botocore.exceptions import ClientError


def get_public_access_block(bucket_name):
  """
  Retrieves the PublicAccessBlock configuration for a given S3 bucket.

  Args:
      bucket_name (str): The name of the S3 bucket.

  Returns:
      dict: The PublicAccessBlock configuration or None if error occurs.
  """
  s3 = boto3.client('s3')
  try:
    response = s3.get_public_access_block(Bucket=bucket_name)
    return response['PublicAccessBlockConfiguration']
  except ClientError as e:
    print(f"Error getting PublicAccessBlock for bucket {bucket_name}: {e}")
    return None


def get_bucket_policy(bucket_name):
  """
  Retrieves the bucket policy for a given S3 bucket.

  Args:
      bucket_name (str): The name of the S3 bucket.

  Returns:
      str: The bucket policy or None if no policy exists or error occurs.
  """
  s3 = boto3.client('s3')
  try:
    response = s3.get_bucket_policy(Bucket=bucket_name)
    return response['Policy']
  except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
      return None  # Handle case where no policy exists
    else:
      print(f"Error getting bucket policy for bucket {bucket_name}: {e}")
      return None


def write_bucket_info(bucket_name, public_access_block, bucket_policy):
  """
  Writes PublicAccessBlock and bucket policy information to the screen and a tab-delimited text file.

  Args:
      bucket_name (str): The name of the S3 bucket.
      public_access_block (dict): The PublicAccessBlock configuration (or None).
      bucket_policy (str): The bucket policy or None if no policy exists.
  """
  global has_printed_header  # Declare global variable before function body

  output_string = ""
  if not has_printed_header:  # Check if header has been printed
    output_string = "BucketName\tPublicAccessBlock\tHasBucketPolicy\n"
    has_printed_header = True  # Set to True after printing header
  output_string += f"{bucket_name}\t"
  if public_access_block:
    output_string += "SET\t"
  else:
    output_string += "NOT SET\t"
  output_string += f"{bucket_policy is not None}\n"
  print(output_string)  # Print the formatted string to screen

  # Write to output.txt file
  with open('output-v2.txt', 'a') as file:
    file.write(output_string)


if __name__ == "__main__":
  # Flag to track if header has been printed
  has_printed_header = False

  # Create an S3 client
  s3 = boto3.client('s3')

  # Get a list of all S3 buckets
  try:
    response = s3.list_buckets()
    buckets = response.get('Buckets', [])
  except ClientError as e:
    print(f"Error listing S3 buckets: {e}")
    exit()

  # Iterate through buckets and get PublicAccessBlock configuration and bucket policy
  for bucket in buckets:
    public_access_block = get_public_access_block(bucket['Name'])
    bucket_policy = get_bucket_policy(bucket['Name'])
    write_bucket_info(bucket['Name'], public_access_block, bucket_policy)

  print("Bucket information displayed on screen and written to output.txt")
