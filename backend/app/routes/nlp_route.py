from flask import Blueprint, jsonify
from flask_cors import CORS  # ✅ Import CORS
from app.middleware.auth_middleware import auth_required
from app.nlp.model import upload_audio



nlp_db = Blueprint('nlp', __name__)
CORS(nlp_db, resources={r"/*": {"origins": "*", "methods": ["POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}})

# Protected routes (auth required)
@nlp_db.route('/', methods=['OPTIONS'])
def handle_options():
    """Handle preflight requests"""
    return jsonify({"message": "CORS Preflight OK"}), 200

# ใช้ฟังก์ชัน upload_audio สำหรับ POST
@nlp_db.route('/', methods=['POST'])
def upload_audio_api():
    return upload_audio()
