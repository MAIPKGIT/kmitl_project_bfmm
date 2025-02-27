from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from flask import request, jsonify
from app.models.account import Account
from flask_jwt_extended import get_jwt
from datetime import datetime


def auth_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # ตรวจสอบว่า JWT Token อยู่ใน Request
                verify_jwt_in_request()
                identity = get_jwt_identity()  # ดึงข้อมูลจาก identity ใน JWT Token

                # ตรวจสอบว่า identity คือ int หรือ dict
                if isinstance(identity, int):  # ถ้า identity เป็นแค่ user_id
                    user_id = identity
                    role_from_jwt = get_jwt()["role"]  # ดึง role จาก claims
                    expires_at = get_jwt()["exp"]  # ดึงเวลาหมดอายุของ token
                elif isinstance(identity, dict) and "id" in identity and "role" in identity:
                    user_id = identity["id"]
                    role_from_jwt = identity["role"]
                    expires_at = get_jwt()["exp"]  # ดึงเวลาหมดอายุของ token
                else:
                    return jsonify({"message": "Invalid token identity!"}), 403

                # ตรวจสอบว่า token หมดอายุหรือยัง
                current_time = datetime.utcnow()
                if current_time.timestamp() > expires_at:
                    return jsonify({"message": "Token has expired!"}), 401

                # ตรวจสอบ Role (ถ้ากำหนด)
                if role and role_from_jwt != role:
                    return jsonify({"message": "Unauthorized access!"}), 403

                # ตรวจสอบผู้ใช้ในฐานข้อมูล (optional)
                user = Account.query.get(user_id)
                if not user:
                    return jsonify({"message": "User not found!"}), 403

            except Exception as e:
                return jsonify({"message": f"Token is invalid! Error: {str(e)}"}), 403
            print(f"Identity: {identity}")
            print(f"JWT: {get_jwt()}")
            print(request.headers.get("Authorization"))
            return fn(*args, **kwargs)
        return decorator
    return wrapper
