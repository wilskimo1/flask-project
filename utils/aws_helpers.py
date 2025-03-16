import boto3
import json

# AWS Secrets Manager Config
SECRET_ARN = "arn:aws:secretsmanager:us-east-1:529088269091:secret:AWS_Cost_Tracker_Credentials-oyUCVy"

def get_aws_credentials():
    """Fetch AWS credentials securely from AWS Secrets Manager."""
    try:
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=SECRET_ARN)
        secret_data = json.loads(response["SecretString"])
        return secret_data["AWS_ACCESS_KEY_ID"], secret_data["AWS_SECRET_ACCESS_KEY"]
    except Exception as e:
        print(f"❌ Error fetching secrets: {e}")
        return None, None

# Get AWS credentials
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = get_aws_credentials()

# Validate if credentials are retrieved
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("❌ AWS Credentials not retrieved. Check Secrets Manager.")

# AWS Configuration
AWS_REGION = "us-east-1"
DYNAMODB_TABLE_NAME = "resume_data"
S3_BUCKET_NAME = "skimos-flask-app"  # ✅ Ensure this is set correctly

# Initialize AWS Clients
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_file_to_s3(file, filename, bucket_name=S3_BUCKET_NAME):
    """Uploads a file to S3 and returns the file URL"""
    try:
        s3_client.upload_fileobj(file, bucket_name, filename)
        file_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return {"message": "File uploaded successfully", "file_url": file_url}
    except Exception as e:
        return {"error": str(e)}

def list_files_in_s3(bucket_name=S3_BUCKET_NAME):
    """Lists all files in the S3 bucket"""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        # ✅ Handle empty bucket scenario
        if "Contents" not in response:
            return []  # Return an empty array instead of None

        files = [
            {
                "name": obj["Key"],
                "size": obj["Size"],
                "url": f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
            }
            for obj in response["Contents"]
        ]
        return files
    except Exception as e:
        return {"error": str(e)}

def delete_file_from_s3(filename, bucket_name=S3_BUCKET_NAME):
    """Deletes a file from S3"""
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=filename)
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
