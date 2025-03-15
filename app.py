from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for
import os, random, requests
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import config  # Import your secure credentials (if using config.py)
from projects.aws_cost_tracker import aws_cost_tracker_bp  # Import the function
from projects.flask_resume_api import flask_resume_api_bp  # ✅ Resume API
from projects.it_compliance_auditor import it_compliance_auditor_bp  # ✅ Import
from projects.infra_monitoring import infra_monitoring_bp
#from utils.aws_helpers import dynamodb, table  # ✅ Import from aws_helpers.py
from datetime import timedelta


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.urandom(24)  

app.config["SESSION_PERMANENT"] = False  # ✅ Default session expires when browser closes
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=1)  # ✅ "Remember Me" lasts for 1 day

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ✅ Make Flask-Login return a JSON error instead of redirecting to login page
@login_manager.unauthorized_handler
def unauthorized_callback():
    return jsonify({"error": "User is not authenticated"}), 403  # 👈 Now returns JSON instead of redirecting

# Import Blueprints (modularized projects)
from projects.aws_cost_tracker import aws_cost_tracker_bp
from projects.flask_resume_api import flask_resume_api_bp
from projects.it_compliance_auditor import it_compliance_auditor_bp
from projects.infra_monitoring import infra_monitoring_bp
from projects.s3_file_manager import s3_file_manager_bp  # ✅ Import S3 File Manager
from projects.chatbot import chatbot_bp
from projects.weather_application import weather_bp


# Register Blueprints
app.register_blueprint(aws_cost_tracker_bp, url_prefix="/aws-cost")
app.register_blueprint(flask_resume_api_bp, url_prefix="/resume")
app.register_blueprint(it_compliance_auditor_bp, url_prefix="/it-compliance")
app.register_blueprint(infra_monitoring_bp, url_prefix="/infra-monitoring")
app.register_blueprint(s3_file_manager_bp, url_prefix="/")
app.register_blueprint(chatbot_bp, url_prefix="/api")
app.register_blueprint(weather_bp, url_prefix="/weather")

# Directory for knowledge repository documents
KNOWLEDGE_REPO_DIR = "static/knowledge_docs"

# GitHub Configuration
GITHUB_USERNAME = "wilskimo1"
GITHUB_REPO = "flask-project"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/commits"


class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# 🔒 Admin Login Route with Dynamic Redirects
@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next")  # Capture the original requested page

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form.get("next")  # Get next_page from form
        remember = request.form.get("remember") == "on"  # ✅ Capture "Remember Me"

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            user = User(id=username)
            login_user(user, remember=remember)  # ✅ Enable "Remember Me" persistence

            # ✅ Ensure next_page is valid and not empty
            if next_page and next_page != "None":
                # ✅ Handle redirection based on requested project page
                if "/projects/infra-monitoring-dashboard/page" in next_page:
                    return redirect(url_for("infra_monitoring.monitoring_dashboard"))  # ✅ Redirect to monitoring

                if "/projects/flask-resume-api/page" in next_page:
                    return redirect(url_for("flask_resume_api.resume_page"))  # ✅ Redirect to resume

                if "/projects/s3-file-manager/page" in next_page:
                    return redirect(url_for("s3_file_manager.s3_dashboard"))  # ✅ Redirect to S3 File Manager

                return redirect(next_page)  # ✅ Default redirect to requested page
            
            return redirect(url_for("projects_page"))  # ✅ Default to projects list if no next_page

        return "Invalid credentials. Try again."

    return render_template("login.html", next_page=next_page)



# 🔓 Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))  # ✅ Redirects to home instead of a specific project

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
        "short_description": "This Project was removed.",
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
        "id": "weather-dashboard",
        "title": "Interactive Weather Reporting Dashboard",
        "technologies": "Flask | OpenWeather API | JavaScript | Bootstrap",
        "short_description": "A dynamic web-based dashboard for real-time weather updates.",
        "detailed_description": "This weather dashboard fetches and displays real-time weather data using the OpenWeather API. Users can search for cities, view current conditions, and access a five-day forecast with temperature, humidity, and wind details. The dashboard features an interactive UI with automatic data refresh and location-based weather retrieval.",
        "commercial_use_case": "Ideal for travel planning, outdoor event management, and integrating into smart home weather monitoring solutions."
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
    
    # Redirect AWS Cost Tracker to the correct route
    if project_id == "aws-cost":
        return redirect(url_for("aws_cost_tracker.aws_cost_page"))  # ✅ Redirect to Blueprint route

    # Map other projects to their templates
    template_map = {
        "flask-resume-api": "flask_resume_api.html",
        "it-compliance-auditor": "it_compliance_auditor.html",
        "infra-monitoring-dashboard": "infra_monitoring_dashboard.html",
        "s3-file-manager": "s3_file_manager.html",
        "serverless-chatbot": "serverless_chatbot.html",
        "weather-dashboard": "weather_dashboard.html",  # ✅ Added Weather Dashboard
        "flask-aws-deployment": "flask_aws_deployment.html"
    }

    template_name = template_map.get(project_id)

    if not template_name:
        return "Project page not found", 404

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


# 🚀 Run Flask App
if __name__ == "__main__":
    app.run(debug=False)
