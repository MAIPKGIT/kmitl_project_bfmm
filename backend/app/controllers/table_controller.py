import random
import string
from app.models.table import Table
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt

# Validate Input Function
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create Table
def create_table():
    try:
        data = request.get_json()
        required_keys = ["people", "status", "code"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        people = data["people"]
        status = data["status"]
        code = data["code"]

        # Prevent Invalid Data
        if status not in ["enable", "disable"]:
            return jsonify({"message": "Status must be 'enable' or 'disable'!"}), 400

        new_table = Table(
            people=people,
            status=status,
            code=code
        )
        db.session.add(new_table)
        db.session.commit()

        return jsonify({"message": "Table created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All Tables
def get_all_tables():
    try:
        tables = Table.query.all()
        # print(f"JWT: {get_jwt()}")
        print(request.headers.get("Authorization"))
        return jsonify([table.as_dict() for table in tables]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get Table by ID
def get_table_by_id(table_id):
    try:
        table = Table.query.get(table_id)
        if table:
            return jsonify(table.as_dict()), 200
        return jsonify({"message": "Table not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get Tables by Code
def get_tables_by_code(code):
    try:
        table = Table.query.filter_by(code=code).first()
        if table:
            return jsonify(table.as_dict()), 200
        return jsonify({"message": "No tables found for this code!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update Table
def update_table(table_id):
    try:
        data = request.get_json()
        table = Table.query.get(table_id)
        if table:
            table.people = data.get("people", table.people)
            table.status = data.get("status", table.status)
            table.code = data.get("code", table.code)

            # Prevent Invalid Data
            if "status" in data and data["status"] not in ["enable", "disable"]:
                return jsonify({"message": "Status must be 'enable' or 'disable'!"}), 400

            db.session.commit()
            return jsonify({"message": "Table updated successfully!"}), 200
        return jsonify({"message": "Table not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete Table
def delete_table(table_id):
    try:
        table = Table.query.get(table_id)
        if table:
            db.session.delete(table)
            db.session.commit()
            return jsonify({"message": "Table deleted successfully!"}), 200
        return jsonify({"message": "Table not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# ฟังก์ชันสุ่มตัวอักษรและตัวเลข
def generate_code():
    existing_codes = {table.code for table in Table.query.with_entities(Table.code).all()}
    
    while True:
        new_code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        if new_code not in existing_codes:
            return new_code

# Update Status Table (Enable/Disable)
def update_status_table():
    try:
        data = request.get_json()
        required_keys = ["table", "people", "status"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        table_number = data["table"]
        people = data["people"]
        status = data["status"]

        # ตรวจสอบสถานะ
        if status not in ["enable", "disable"]:
            return jsonify({"message": "Status must be 'enable' or 'disable'!"}), 400

        # หาข้อมูลโต๊ะ
        table = Table.query.get(table_number)
        if not table:
            return jsonify({"message": "Table not found!"}), 404

        # ตรวจสอบสถานะของโต๊ะก่อน ถ้าสถานะตรงกับที่ส่งมาแล้ว ให้แจ้งเตือน
        if table.status == status:
            return jsonify({"message": f"Table is already {status}d!"}), 400

        # เปลี่ยนสถานะเป็น enable
        if status == "enable":
            table.people = people
            table.code = generate_code()  # สุ่มรหัสเมื่อสถานะเป็น enable
            table.status = "enable"
        else:  # ถ้าสถานะเป็น disable
            table.people = None  # ลบข้อมูล people
            table.code = None  # ลบข้อมูล code
            table.status = "disable"

        db.session.commit()

        # ส่ง code กลับไปพร้อมกับข้อความ
        return jsonify({
            "message": f"Table {status}d successfully!",
            "code": table.code  # ส่ง code กลับไป
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
    

