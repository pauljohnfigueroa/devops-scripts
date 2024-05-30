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


def write_public_access_info(bucket_name, public_access_block):
  """
  Writes PublicAccessBlock information to the screen and a tab-delimited text file.

  Args:
      bucket_name (str): The name of the S3 bucket.
      public_access_block (dict): The PublicAccessBlock configuration (or None).
  """
  global has_printed_header  # Declare global variable before function body

  output_string = ""
  if not has_printed_header:  # Check if header has been printed
    output_string = "BucketName\tBlockPublicAcls\tIgnorePublicAcls\tBlockPublicPolicy\tRestrictPublicBuckets\n"
    has_printed_header = True  # Set to True after printing header
  output_string += f"{bucket_name}\t"
  if public_access_block:
    # Extract relevant data from PublicAccessBlock configuration
    block_public_acls = public_access_block.get('BlockPublicAcls', 'NOT SET')
    ignore_public_acls = public_access_block.get('IgnorePublicAcls', 'NOT SET')
    block_public_policy = public_access_block.get('BlockPublicPolicy', 'NOT SET')
    restrict_public_buckets = public_access_block.get('RestrictPublicBuckets', 'NOT SET')
    output_string += f"{block_public_acls}\t{ignore_public_acls}\t{block_public_policy}\t{restrict_public_buckets}\n"
  else:
    output_string += "ERROR\tERROR\tERROR\tERROR\n"
  print(output_string)  # Print the formatted string to screen
  
  # Write to output.txt file
  with open('output.txt', 'a') as file:
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

  # Iterate through buckets and get PublicAccessBlock configuration
  for bucket in buckets:
    public_access_block = get_public_access_block(bucket['Name'])
    write_public_access_info(bucket['Name'], public_access_block)

  print("Public access information displayed on screen and written to output.txt")
