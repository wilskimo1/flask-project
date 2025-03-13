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

# AWS Configuration (Assuming credentials are stored in Secrets Manager)
AWS_REGION = "us-east-1"
DYNAMODB_TABLE_NAME = "resume_data"

# Initialize DynamoDB and CloudWatch clients
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)  # ✅ Add this line