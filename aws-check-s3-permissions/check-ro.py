import json
import boto3
from botocore.exceptions import ClientError

def check_bucket_read_only(bucket_name):
    s3_client = boto3.client('s3')

    try:
        # Get bucket policy
        bucket_policy = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(bucket_policy['Policy'])

        statements = policy.get('Statement', [])

        read_only = False
        for statement in statements:
            effect = statement.get('Effect')
            principal = statement.get('Principal')
            action = statement.get('Action')
            resource = statement.get('Resource')

            # Check if Effect is Allow
            if effect == 'Allow':
                # Check if Principal is "*", meaning it's public
                if principal == "*" or (isinstance(principal, dict) and principal.get("AWS") == "*"):
                    # Check if Action includes s3:GetObject
                    if action == "s3:GetObject" or (isinstance(action, list) and "s3:GetObject" in action):
                        # Check if Resource matches the bucket's objects
                        if resource == f"arn:aws:s3:::{bucket_name}/*" or (isinstance(resource, list) and f"arn:aws:s3:::{bucket_name}/*" in resource):
                            read_only = True
                            break

        if read_only:
            print(f"Bucket {bucket_name} is publicly readable (read-only access).")
        else:
            print(f"Bucket {bucket_name} is not publicly readable.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            print(f"Bucket {bucket_name} has no bucket policy.")
        else:
            print(f"Error fetching bucket policy for {bucket_name}: {e}")

if __name__ == "__main__":
    bucket_name = input("Enter the S3 bucket name: ")
    check_bucket_read_only(bucket_name)
