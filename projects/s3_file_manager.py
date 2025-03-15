from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from utils.aws_helpers import s3, S3_BUCKET_NAME

# Create Blueprint
s3_file_manager_bp = Blueprint("s3_file_manager", __name__, template_folder="templates")

# ✅ Route: S3 File Manager Dashboard (Requires Login)
@s3_file_manager_bp.route("/s3-file-manager")
@login_required
def s3_dashboard():
    """Render S3 File Manager Page."""
    return render_template("s3_file_manager.html", is_admin=current_user.is_authenticated)

# ✅ Route: List Files in S3
@s3_file_manager_bp.route("/api/s3/list", methods=["GET"])
def list_files():
    """List files in the S3 bucket."""
    if not current_user.is_authenticated:
        return jsonify({"error": "User is not authenticated"}), 401  # ✅ Return 401 instead of redirect

    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
        files = [
            {
                "name": obj["Key"],
                "size": obj["Size"],
                "url": f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{obj['Key']}"
            }
            for obj in response.get("Contents", [])
        ]
        return jsonify(files)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route: Upload File to S3
@s3_file_manager_bp.route("/api/s3/upload", methods=["POST"])
def upload_file():
    """Upload a file to S3."""
    if not current_user.is_authenticated:
        return jsonify({"error": "User is not authenticated"}), 401  # ✅ Return 401 instead of redirect

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    file_name = file.filename

    if file_name == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        s3.upload_fileobj(file, S3_BUCKET_NAME, file_name)
        return jsonify({"message": "File uploaded successfully", "file_name": file_name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route: Delete File from S3
@s3_file_manager_bp.route("/api/s3/delete", methods=["POST"])
def delete_file():
    """Delete a file from S3."""
    if not current_user.is_authenticated:
        return jsonify({"error": "User is not authenticated"}), 401  # ✅ Return 401 instead of redirect

    data = request.get_json()
    file_name = data.get("file_name")

    if not file_name:
        return jsonify({"error": "Missing file name"}), 400

    try:
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=file_name)
        return jsonify({"message": f"File '{file_name}' deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
