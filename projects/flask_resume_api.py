from flask import Blueprint, render_template, request, jsonify
import boto3
from flask_login import login_required, current_user
from utils.aws_helpers import dynamodb  # ✅ Import DynamoDB instance

flask_resume_api_bp = Blueprint("flask_resume_api", __name__)  # ✅ Define the Blueprint

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("resume_data")

### ✅ Publicly Accessible Resume Page (No Login Required)
@flask_resume_api_bp.route("/")
def resume_page():
    """Render the Resume page."""
    return render_template("flask_resume_api.html", is_admin=current_user.is_authenticated)

### ✅ Publicly Accessible API to Read Resume (No Login Required)
@flask_resume_api_bp.route("/api/resume", methods=["GET"])
def get_resume():
    """Fetch resume details from DynamoDB (Public API)."""
    try:
        response = table.get_item(Key={"user_id": "1"})  # Hardcoded user_id for now
        print(f"🔍 DynamoDB Response: {response}")  # ✅ Debugging Output

        if "Item" in response:
            return jsonify(response["Item"])
        else:
            return jsonify({"error": "No resume data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flask_resume_api_bp.route("/api/resume", methods=["POST"])
@login_required  # ✅ Restricts updates to logged-in users
def update_resume():
    """Update resume details in DynamoDB (Partial Updates Allowed)."""

    data = request.json  # Incoming JSON data
    try:
        # ✅ Step 1: Fetch existing resume data
        response = table.get_item(Key={"user_id": "1"})  
        existing_data = response.get("Item", {})

        if not existing_data:
            return jsonify({"error": "No existing resume data found"}), 404

        # ✅ Step 2: Merge new data with old data (only update fields that are sent)
        updated_resume = {
            "user_id": "1",  # Keep user_id constant
            "name": data.get("name", existing_data.get("name")),
            "email": data.get("email", existing_data.get("email")),
            "phone": data.get("phone", existing_data.get("phone")),
            "experience": data.get("experience", existing_data.get("experience")),
            "skills": data.get("skills", existing_data.get("skills")),
        }

        # ✅ Step 3: Save updated resume back to DynamoDB
        table.put_item(Item=updated_resume)

        return jsonify({
            "message": "Resume updated successfully!",
            "updated_data": updated_resume
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

