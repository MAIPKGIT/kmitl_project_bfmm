from app.models.account import Account
from app.schemas.account_schema import AccountSchema
from app import db
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

# Input Validation Function
def validate_input(data, keys):
    for key in keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create Account
def create_account():
    try:
        data = request.get_json()
        required_keys = ["username", "password"]
        is_valid, message = validate_input(data, required_keys)
        if not is_valid:
            return jsonify({"message": message}), 400

        username = data["username"]
        password = data["password"]
        mail = data.get("mail", None)
        phone = data.get("phone", None)
        role = data.get("role", "member")

        # Check for duplicate username
        if Account.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists!"}), 409

        # Hash password
        hashed_password = generate_password_hash(password)

        new_account = Account(username=username, password=hashed_password, mail=mail, phone=phone, role=role)
        db.session.add(new_account)
        db.session.commit()

        return jsonify({"message": "Account created successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Get All Accounts
@jwt_required()
def get_all_accounts():
    try:
        accounts = Account.query.all()
        return jsonify(accounts_schema.dump(accounts)), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Get Account by ID
@jwt_required()
def get_account_by_id(account_id):
    try:
        account = Account.query.get(account_id)
        if account:
            return jsonify(account_schema.dump(account)), 200
        return jsonify({"message": "Account not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Update Account
@jwt_required()
def update_account(account_id):
    try:
        data = request.get_json()
        account = Account.query.get(account_id)
        if account:
            account.username = data.get('username', account.username)
            if "password" in data:
                account.password = generate_password_hash(data['password'])
            account.mail = data.get('mail', account.mail)
            account.phone = data.get('phone', account.phone)
            account.role = data.get('role', account.role)

            db.session.commit()
            return jsonify({"message": "Account updated successfully!"}), 200
        return jsonify({"message": "Account not found!"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Delete Account
@jwt_required()
def delete_account(account_id):
    try:
        account = Account.query.get(account_id)
        if account:
            db.session.delete(account)
            db.session.commit()
            return jsonify({"message": "Account deleted successfully!"}), 200
        return jsonify({"message": "Account not found!"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Login
def login():
    try:
        data = request.get_json()
        required_keys = ["username", "password"]
        is_valid, message = validate_input(data, required_keys)
        if not is_valid:
            return jsonify({"message": message}), 400

        username = data["username"]
        password = data["password"]

        # Check user existence
        account = Account.query.filter_by(username=username).first()
        if not account or not check_password_hash(account.password, password):
            return jsonify({"message": "Invalid credentials!"}), 401

        # Generate JWT token with additional claims
        additional_claims = {"role": account.role}
        access_token = create_access_token(identity=account.id, additional_claims=additional_claims, expires_delta=timedelta(hours=12))

        return jsonify({"   ": access_token}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Logout
@jwt_required()
def logout():
    try:
        response = jsonify({"message": "Successfully logged out!"})
        # Unset JWT cookies to log out the user
        unset_jwt_cookies(response)
        return response, 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

