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
            return "Publicly Readable (Read-Only)"
        else:
            return "Not Publicly Readable"

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return "No Bucket Policy"
        else:
            return f"Error: {e.response['Error']['Message']}"

def get_all_buckets():
    s3_client = boto3.client('s3')
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return buckets
    except ClientError as e:
        print(f"Error listing buckets: {e}")
        return []

if __name__ == "__main__":
    buckets = get_all_buckets()
    if buckets:
        with open("output-ro-v2.txt", "w") as f:
            f.write("Bucket Name\tPermission\n")
            print(f"{'Bucket Name':<40} {'Permission':<40}")
            print("="*80)
            for bucket in buckets:
                permission = check_bucket_read_only(bucket)
                f.write(f"{bucket}\t{permission}\n")
                print(f"{bucket:<40} {permission:<40}")
        print("\nOutput written to output-ro-v2.txt")
    else:
        print("No buckets found.")
