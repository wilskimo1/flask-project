from flask import Flask, render_template, jsonify, send_from_directory
import os, random, requests

app = Flask(__name__)

# Directory for knowledge repository documents
KNOWLEDGE_REPO_DIR = "static/knowledge_docs"

# GitHub Configuration
GITHUB_USERNAME = "wilskimo1"
GITHUB_REPO = "flask-project"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/commits"

# Full Project Data (All 9 Projects)
projects = [
    {
        "id": "aws-cost-tracker",
        "title": "AWS Cost Tracker",
        "technologies": "Flask | DynamoDB | AWS Lambda",
        "short_description": "Monitors AWS spending & sends alerts.",
        "detailed_description": "A cloud-based tool that continuously monitors AWS usage costs, providing real-time alerts when spending exceeds budgeted limits.",
        "commercial_use_case": "Useful for IT teams managing cloud budgets, ensuring cost efficiency and preventing unexpected overages."
    },
    {
        "id": "flask-resume-api",
        "title": "Flask Resume API",
        "technologies": "Flask | PostgreSQL",
        "short_description": "Dynamically fetches and updates resume data.",
        "detailed_description": "A REST API that allows dynamic updates and retrieval of resume details stored in a database.",
        "commercial_use_case": "Ideal for job portals, recruiters, and professionals wanting a dynamically updated online resume."
    },
    {
        "id": "python-ai-assistant",
        "title": "Python AI Assistant",
        "technologies": "Flask | OpenAI API",
        "short_description": "AI-powered responses and automation.",
        "detailed_description": "A chatbot capable of answering technical and business-related questions using AI-generated responses.",
        "commercial_use_case": "Useful for customer service automation, technical support, and AI-powered productivity tools."
    },
    {
        "id": "it-compliance-auditor",
        "title": "IT Compliance Auditor",
        "technologies": "Flask | AWS Security Hub",
        "short_description": "Scans AWS for compliance violations.",
        "detailed_description": "Automatically evaluates AWS resources against compliance frameworks like CIS, NIST, and PCI-DSS.",
        "commercial_use_case": "Helps security teams maintain AWS compliance and prevent security risks."
    },
    {
        "id": "infra-monitoring-dashboard",
        "title": "Infrastructure Monitoring",
        "technologies": "Flask | Dash | CloudWatch",
        "short_description": "Real-time AWS resource monitoring.",
        "detailed_description": "A web-based dashboard that visualizes AWS infrastructure performance metrics in real-time.",
        "commercial_use_case": "Used by IT operations teams to monitor system health, detect anomalies, and optimize infrastructure performance."
    },
    {
        "id": "log-analyzer",
        "title": "Log Analyzer & Error Tracker",
        "technologies": "Flask | ELK Stack | Machine Learning",
        "short_description": "Detects system anomalies and logs errors.",
        "detailed_description": "Utilizes machine learning to analyze system logs, detect patterns, and generate real-time alerts for critical failures.",
        "commercial_use_case": "Used by DevOps and IT support teams for proactive issue resolution and log management automation."
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
        "detailed_description": "A Python desktop application with an intuitive graphical user interface (GUI) that syncs data with a Flask-powered API.",
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

# 🏠 Homepage Route
@app.route("/")
def home():
    return render_template("index.html")

# Ensure Flask serves static files (especially `scripts.js` and `styles.css`)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 📂 Projects API Route - Fetch all projects
@app.route("/api/projects", methods=["GET"])
def get_projects():
    return jsonify(projects)

# 🔍 Projects API Route - Fetch specific project by ID
@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project)

# 🏗️ Projects Page
@app.route("/projects")
def projects_page():
    return render_template("projects.html", projects=projects)

# 📑 Deployment Documentation Page
@app.route("/deployment-docs")
def deployment_docs():
    return render_template("deployment_docs.html")

# 📝 Individual Project Details Page
@app.route("/projects/<project_id>")
def project_detail(project_id):
    return render_template("project_details.html")

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
