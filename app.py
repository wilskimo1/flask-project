from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for
import os, random, requests, boto3, json, datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import config  # Import your secure credentials (if using config.py)


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.secret_key = os.urandom(24)  

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# AWS Configuration (Assuming credentials are stored in Secrets Manager)
AWS_REGION = "us-east-1"
DYNAMODB_TABLE_NAME = "resume_data"

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Directory for knowledge repository documents
KNOWLEDGE_REPO_DIR = "static/knowledge_docs"

# GitHub Configuration
GITHUB_USERNAME = "wilskimo1"
GITHUB_REPO = "flask-project"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/commits"

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

# Initialize AWS Cost Explorer client
ce_client = boto3.client(
    "ce",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1"
)

# 🔹 Function to fetch AWS cost data (Fixed for dynamic dates)
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

# 📂 AWS Cost Tracker Route (Updated template name)
@app.route("/aws-cost-tracker")
def aws_cost_tracker():
    """Display AWS cost data in UI."""
    current_cost = get_aws_cost()
    
    if current_cost is None:
        alert_status = "⚠️ Unable to retrieve AWS cost data."
        current_cost = "N/A"
    elif current_cost > 100:
        alert_status = "🚨 ALERT: Budget Exceeded!"
    else:
        alert_status = "✅ OK - Currently within Budget"

    #print(f"🖥️ Debug: Cost = {current_cost}, Alert Status = {alert_status}")  # Debugging Output

    return render_template("aws_cost_tracker.html", cost=current_cost, alert_status=alert_status)


class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# 🔒 Admin Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            user = User(id=username)
            login_user(user)
            return redirect(url_for("resume_page"))  # Redirect to resume page

        return "Invalid credentials. Try again."

    return render_template("login.html")

# 🔓 Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("resume_page"))

# Project Data
projects = [
    {
        "id": "aws-cost", "title": "AWS Cost Tracker", "technologies": "Flask | DynamoDB | AWS Lambda",
     "short_description": "Monitors AWS spending & sends alerts.",
     "detailed_description": "A cloud-based tool that continuously monitors AWS usage costs, providing real-time alerts when spending exceeds budgeted limits.",
     "commercial_use_case": "Useful for IT teams managing cloud budgets, ensuring cost efficiency and preventing unexpected overages."
    },
    {
        "id": "flask-resume-api", "title": "Flask Resume API", "technologies": "Flask | PostgreSQL",
     "short_description": "Dynamically fetches and updates resume data.",
     "detailed_description": "A REST API that allows dynamic updates and retrieval of resume details stored in a database.",
     "commercial_use_case": "Ideal for job portals, recruiters, and professionals wanting a dynamically updated online resume."
    },
    {
        "id": "it-compliance-auditor", "title": "IT Compliance Auditor", "technologies": "Flask | AWS Security Hub",
     "short_description": "Scans AWS for compliance violations.",
     "detailed_description": "Automatically evaluates AWS resources against compliance frameworks like CIS, NIST, and PCI-DSS.",
     "commercial_use_case": "Helps security teams maintain AWS compliance and prevent security risks."
    },
    {
        "id": "infra-monitoring-dashboard", "title": "Infrastructure Monitoring", "technologies": "Flask | Dash | AWS CloudWatch",
     "short_description": "Real-time AWS resource monitoring.",
     "detailed_description": "A web-based dashboard that visualizes AWS infrastructure performance metrics in real-time.",
     "commercial_use_case": "Used by IT operations teams to monitor system health, detect anomalies, and optimize infrastructure performance."
    },
    {
        "id": "log-analyzer",
        "title": "Log Analyzer & Error Tracker",
        "technologies": "Flask | ELK Stack",
        "short_description": "Detects system anomalies and logs errors.",
        "detailed_description": "Analyzes system logs, detects patterns, and generates real-time alerts for critical failures.",
        "commercial_use_case": "Used by DevOps and IT support teams for proactive issue resolution and log management automation."
    },
    {
        "id": "s3-file-manager",
        "title": "S3 File Manager",
        "technologies": "Flask | AWS S3 | Boto3",
        "short_description": "Upload, delete, and manage files on S3.",
        "detailed_description": "A web-based interface for managing files in Amazon S3, allowing users to upload, list, and delete objects from an S3 bucket.",
        "commercial_use_case": "Useful for businesses managing static assets, backups, or large-scale file storage."
    },
    {
        "id": "serverless-chatbot",
        "title": "Serverless Chatbot",
        "technologies": "AWS Lambda | API Gateway | Flask",
        "short_description": "Automated chatbot using serverless architecture.",
        "detailed_description": "A lightweight serverless chatbot that provides automated responses and integrates with messaging platforms.",
        "commercial_use_case": "Useful for customer support automation, business FAQs, and internal HR chatbots."
    },
    {
        "id": "tkinter-desktop-app",
        "title": "Tkinter-based Desktop App",
        "technologies": "Tkinter | Flask API | SQLite",
        "short_description": "Local GUI app syncing with a Flask API.",
        "detailed_description": "A Python desktop application with an intuitive GUI that syncs data with a Flask-powered API.",
        "commercial_use_case": "Ideal for local inventory management, personal finance tracking, and offline applications that sync with the cloud."
    },
    {
        "id": "flask-aws-deployment",
        "title": "Flask Website Deployment & AWS Infrastructure",
        "technologies": "Flask | AWS EC2 | Auto Scaling | RDS | S3 | CloudFront | GitHub Actions",
        "short_description": "End-to-end cloud deployment with CI/CD.",
        "detailed_description": "A full-stack cloud deployment project demonstrating Flask hosting on AWS, utilizing infrastructure-as-code for scalable, high-availability deployment.",
        "commercial_use_case": "Ideal for businesses transitioning to AWS for scalable web hosting, incorporating cost-efficient CI/CD automation and cloud-native best practices."
    }
]

# 🏠 Homepage
@app.route("/")
def home():
    return render_template("index.html")

# 📂 Projects List Page (Shows all projects as cards)
@app.route("/projects")
def projects_page():
    return render_template("projects.html", projects=projects)

@app.route("/projects/<project_id>/page")
def project_page(project_id):
    """Serve the actual project page if the template exists and pass required data."""
    
    template_map = {
        "aws-cost": "aws_cost_tracker.html",
        "flask-resume-api": "flask_resume_api.html",
        "it-compliance-auditor": "it_compliance_auditor.html",
        "infra-monitoring-dashboard": "infra_monitoring_dashboard.html",
        "log-analyzer": "log_analyzer.html",
        "s3-file-manager": "s3_file_manager.html",
        "serverless-chatbot": "serverless_chatbot.html",
        "tkinter-desktop-app": "tkinter_desktop_app.html",
        "flask-aws-deployment": "flask_aws_deployment.html"
    }

    template_name = template_map.get(project_id)

    if not template_name:
        return "Project page not found", 404

    # 🟢 Fix: AWS Cost Tracker uses the latest message format
    if project_id == "aws-cost":
        current_cost = get_aws_cost()
        if current_cost is None:
            return "Error retrieving AWS cost data."

        if current_cost > 100:
            alert_status = "🚨 ALERT: Budget Exceeded!"
        else:
            alert_status = "✅ OK - Currently within Budget"  # Updated message!

        return render_template(template_name, cost=current_cost, alert_status=alert_status)

    # 🟢 For all other projects, just render the template
    return render_template(template_name)


# 📑 Deployment Documentation Page
@app.route("/deployment-docs")
def deployment_docs():
    return render_template("deployment_docs.html")

# 🔍 Route for Specific Project Page
@app.route("/projects/<project_id>")
def project_detail(project_id):
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return "Project not found", 404
    return render_template("project_details.html", project=project)

# 📚 Knowledge Repository Route
@app.route("/knowledge")
def knowledge_repository():
    try:
        documents = os.listdir(KNOWLEDGE_REPO_DIR)
        documents = [doc for doc in documents if doc.endswith(('.pdf', '.txt', '.docx', '.md'))]  # Filter valid file types
    except FileNotFoundError:
        documents = []
    return render_template("knowledge.html", documents=documents)

# 📥 Knowledge Repository - File Download
@app.route("/knowledge/download/<filename>")
def download_document(filename):
    return send_from_directory(KNOWLEDGE_REPO_DIR, filename, as_attachment=True)

# View Knowledge Repository Document in Browser
@app.route("/knowledge/view/<filename>")
def view_document(filename):
    return send_from_directory(KNOWLEDGE_REPO_DIR, filename)

# 📂 Experience Page
@app.route("/experience")
def experience():
    return render_template("experience.html")

# 📩 Contact Page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# 🎲 API: Random Number Generator (Example Interactive Feature)
@app.route("/api/random-number", methods=["GET"])
def random_number():
    return jsonify({"random_number": random.randint(1, 100)})

# 📌 New API: Fetch latest GitHub commits
@app.route("/api/github-commits", methods=["GET"])
def get_github_commits():
    try:
        response = requests.get(GITHUB_API_URL)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch commits"}), response.status_code
        
        commits_data = response.json()
        commits = []

        for commit in commits_data[:5]:  # Get the latest 5 commits
            commits.append({
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "url": commit["html_url"]
            })

        return jsonify(commits)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 Fetch Resume API
@app.route("/api/resume", methods=["GET"])
def get_resume():
    """Fetch resume details from DynamoDB."""
    try:
        response = table.get_item(Key={"user_id": "1"})  # Hardcoded user_id for now
        if "Item" in response:
            return jsonify(response["Item"])
        else:
            return jsonify({"error": "No resume data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 Update Resume API
@app.route("/api/resume", methods=["POST"])
def update_resume():
    """Update resume details in DynamoDB (Overwrite Existing Data)."""
    data = request.json  # Get JSON payload from request

    try:
        table.put_item(
            Item={
                "user_id": "1",  # Ensures only one entry for this user
                "name": data["name"],
                "email": data["email"],
                "phone": data["phone"],
                "experience": data["experience"],
                "skills": data["skills"]
            }
        )
        return jsonify({"message": "Resume updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resume")
def resume_page():
    return render_template("flask_resume_api.html", is_admin=current_user.is_authenticated)

# 🚀 Run Flask App
if __name__ == "__main__":
    app.run(debug=False)
