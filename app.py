from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

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

# Homepage Route
@app.route("/")
def home():
    return render_template("index.html")

# Projects Page
@app.route("/projects")
def projects_page():
    return render_template("projects.html", projects=projects)

# Deployment page route
@app.route("/deployment-docs")
def deployment_docs():
    return render_template("deployment_docs.html")

# Individual Project Details
@app.route("/projects/<project_name>")
def project_detail(project_name):
    print(f"Fetching details for project: {project_name}")  # Debugging line

    # Try to find the project in the list
    project = next((p for p in projects if p["id"] == project_name), None)

    if not project:
        print("Error: Project not found")  # Debugging output
        return "Project Not Found", 404

    return render_template("project_details.html", project=project)

# Experience Page
@app.route("/experience")
def experience():
    return render_template("experience.html")

# Contact Page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# API: Random Number Generator
@app.route("/api/random-number", methods=["GET"])
def random_number():
    return jsonify({"random_number": random.randint(1, 100)})

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
