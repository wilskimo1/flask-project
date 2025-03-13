from flask import Blueprint, render_template
import boto3
import datetime
from utils.aws_helpers import get_aws_credentials

aws_cost_tracker_bp = Blueprint("aws_cost_tracker", __name__)

# Get AWS credentials from Secrets Manager
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = get_aws_credentials()

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("❌ AWS Credentials not retrieved. Check Secrets Manager.")

# Initialize AWS Cost Explorer client
ce_client = boto3.client(
    "ce",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1"
)

def get_aws_cost():
    """Retrieve AWS cost data from Cost Explorer."""
    try:
        today = datetime.date.today()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")  # First day of this month
        end_date = today.strftime("%Y-%m-%d")  # Today

        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"]
        )
        cost = response["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]
        return float(cost)
    except Exception as e:
        print(f"❌ Error fetching cost data: {e}")
        return None

@aws_cost_tracker_bp.route("/")
def aws_cost_page():
    """Display AWS cost data in UI."""
    current_cost = get_aws_cost()

    if current_cost is None:
        alert_status = "⚠️ Unable to retrieve AWS cost data."
        current_cost = "N/A"
    elif current_cost > 100:
        alert_status = "🚨 ALERT: Budget Exceeded!"
    else:
        alert_status = "✅ OK - Currently within Budget"

    return render_template("aws_cost_tracker.html", cost=current_cost, alert_status=alert_status)
