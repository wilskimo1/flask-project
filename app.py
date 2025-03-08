from flask import Flask, render_template, jsonify, send_from_directory, request
import os, random, requests, boto3, json
from transformers import pipeline # ✅ Free AI Model for Text Summarization
import yfinance as yf #Yahoo Finance API
from PIL import Image
import io
import easyocr
from facenet_pytorch import MTCNN

app = Flask(__name__)

# Directory for knowledge repository documents
KNOWLEDGE_REPO_DIR = "static/knowledge_docs"

# GitHub Configuration
GITHUB_USERNAME = "wilskimo1"
GITHUB_REPO = "flask-project"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/commits"

# ✅ Load AI Models
image_recognition = pipeline("image-classification", model="facebook/deit-base-distilled-patch16-224")
object_detection = pipeline("object-detection", model="facebook/detr-resnet-50")
face_detection = MTCNN(keep_all=True)  # Initializes the face detector
ocr_reader = easyocr.Reader(['en'])  # OCR Model

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

# 🔹 Function to fetch AWS cost data
def get_aws_cost():
    """Retrieve AWS cost data from Cost Explorer."""
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": "2024-03-01", "End": "2024-03-31"},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"]
        )
        cost = response["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]
        return float(cost)
    except Exception as e:
        print(f"❌ Error fetching cost data: {e}")
        return None



# 📂 AWS Cost Tracker Route
@app.route("/aws-cost")
def aws_cost():
    """Display AWS cost data in UI."""
    current_cost = get_aws_cost()
    if current_cost is None:
        return "Error retrieving AWS cost data."

    alert_status = "✅ OK" if current_cost < 100 else "🚨 ALERT: Budget Exceeded!"
    
    return render_template("aws_cost.html", cost=current_cost, alert_status=alert_status)

# ✅ AI Model: Load Free Text Summarizer (Hugging Face Model)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ✅ AI Model: Load Free Image Recognition Model
image_recognition = pipeline("image-classification", model="facebook/deit-base-distilled-patch16-224")


# ✅ AI API Route - Free Text Summarization
@app.route("/api/summarize", methods=["POST"])
def summarize_text():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return jsonify({"summary": summary[0]["summary_text"]})

    except Exception as e:
        print(f"❌ Error in text summarization: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ AI Tools Routes
@app.route("/ai/text-summarizer")
def text_summarizer():
    return render_template("text_summarizer.html")

@app.route("/api/image-recognition", methods=["POST"])
def recognize_image():
    try:
        data = request.get_json()
        image_url = data.get("image_url", "")

        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400

        # Fetch the image content
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Invalid image URL"}), 400

        # Convert image bytes to a PIL image
        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        # Run AI model
        results = image_recognition(image)

        return jsonify({"labels": results})

    except Exception as e:
        print(f"❌ Error in image recognition: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/stock-predictor", methods=["POST"])
def stock_predictor():
    try:
        data = request.get_json()
        stock_symbol = data.get("stock_symbol", "").upper()  # Ensure symbol is uppercase

        if not stock_symbol:
            return jsonify({"error": "No stock symbol provided"}), 400

        stock = yf.Ticker(stock_symbol)
        history = stock.history(period="1mo")

        if history.empty:
            return jsonify({"error": f"Invalid stock symbol: {stock_symbol} or no data available"}), 400

        latest_price = history["Close"].iloc[-1]

        return jsonify({"stock_symbol": stock_symbol, "latest_price": latest_price})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/object-detection", methods=["POST"])
def detect_objects():
    try:
        data = request.get_json()
        image_url = data.get("image_url", "")

        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400

        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Invalid image URL"}), 400

        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        results = object_detection(image)
        return jsonify({"labels": results})

    except Exception as e:
        print(f"❌ Error in object detection: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/face-recognition", methods=["POST"])
def recognize_faces():
    try:
        data = request.get_json()
        image_url = data.get("image_url", "")

        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400

        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Invalid image URL"}), 400

        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        # Detect faces
        boxes, _ = face_detection.detect(image)

        if boxes is None:
            return jsonify({"faces": []})  # No faces detected

        results = [{"box": box.tolist()} for box in boxes]

        return jsonify({"faces": results})

    except Exception as e:
        print(f"❌ Error in face recognition: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/ocr", methods=["POST"])
def extract_text():
    try:
        data = request.get_json()
        image_url = data.get("image_url", "")

        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400

        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Invalid image URL"}), 400

        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        results = ocr_reader.readtext(image)
        text_results = [entry[1] for entry in results]
        return jsonify({"text": text_results})

    except Exception as e:
        print(f"❌ Error in OCR: {e}")
        return jsonify({"error": str(e)}), 500

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
    
# ✅ AI Tools Routes
@app.route("/ai/text-summarizer")
def text_summarizer_page():
    return render_template("text_summarizer.html")

@app.route("/ai/image-recognition")
def image_recognition_page():
    return render_template("image_recognition.html")

@app.route("/ai/stock-predictor")
def stock_predictor_page():
    return render_template("stock_predictor.html")

# ✅ AI Model: Load Free Text Summarizer (Hugging Face Model)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ✅ AI API Route - Free Text Summarization
@app.route("/api/summarize", methods=["POST"])
def summarize_text_api():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return jsonify({"summary": summary[0]["summary_text"]})

    except Exception as e:
        print(f"❌ Error in text summarization: {e}")
        return jsonify({"error": str(e)}), 500

# 🚀 Run Flask App
if __name__ == "__main__":
    app.run(debug=False)
