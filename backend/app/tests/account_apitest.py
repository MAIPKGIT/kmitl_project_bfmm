from flask import jsonify, request
from app import create_app, db
from app.models.account import Account
from flask_jwt_extended import create_access_token
import json

def index():
    return jsonify({"test": "account"})

# Helper function for adding test cases
def add_test_case(description, result, expected_status, response_data=None, error_message=None):
    if isinstance(result, dict):  # กรณีที่ result เป็น dictionary
        # ในกรณีนี้ result จะเป็น dictionary ที่เราใช้เก็บข้อมูล access_token
        passed = "access_token" in result and result.get("access_token") is not None
        status_code = 200 if passed else 401  # ถ้ามี access_token ถือว่า successful (200)
        response_data = result  # เก็บข้อมูลของ result เอาไว้ใน response_data
    else:  # กรณีที่ result เป็น response object (เช่น จากการทดสอบ API)
        passed = result.status_code == expected_status
        status_code = result.status_code
        response_data = result.json() if response_data else None

    return {
        "description": description,
        "passed": passed,
        "status_code": status_code,
        "expected_status": expected_status,
        "response_data": response_data,
        "error_message": error_message
    }

def create_account(client):
    try:
        account_data = {
            "username": "unittest1",
            "password": "unittest1",
            "mail": "unittest1@example.com",
            "phone": "1234567890",
            "role": "admin"
        }
        response = client.post('/api/account/', data=json.dumps(account_data), content_type='application/json')
        return add_test_case("Create a new account", response, 201)
    except Exception as e:
        return add_test_case("Create a new account", None, 201, error_message=str(e))


def duplicate_account_creation(client):
    try:
        account_data = {
            "username": "unittest1",
            "password": "unittest1",
            "mail": "unittest1@example.com",
            "phone": "1234567890",
            "role": "admin"
        }
        response = client.post('/api/account/', data=json.dumps(account_data), content_type='application/json')
        return add_test_case("Attempt to create a duplicate account", response, 409)
    except Exception as e:
        return add_test_case("Attempt to create a duplicate account", None, 409, error_message=str(e))


def get_all_accounts_without_auth(client):
    try:
        response = client.get('/api/account/')
        return add_test_case("Get all accounts without authentication", response, 401)
    except Exception as e:
        return add_test_case("Get all accounts without authentication", None, 401, error_message=str(e))


def login_and_get_token(client):
    try:
        login_data = {
            "username": "unittest1",
            "password": "unittest1"
        }
        response = client.post('/api/account/login', data=json.dumps(login_data), content_type='application/json')
        if response.status_code == 200:
            return response.json.get('access_token')
        else:
            return None
    except Exception as e:
        return None



def get_all_accounts_with_auth(client, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get('/api/account/', headers=headers)
        return add_test_case("Get all accounts with authentication", response, 200)
    except Exception as e:
        return add_test_case("Get all accounts with authentication", None, 200, error_message=str(e))


def invalid_login(client):
    try:
        invalid_login_data = {
            "username": "invaliduser",
            "password": "wrongpassword"
        }
        response = client.post('/api/account/login', data=json.dumps(invalid_login_data), content_type='application/json')
        return add_test_case("Invalid login attempt", response, 401)
    except Exception as e:
        return add_test_case("Invalid login attempt", None, 401, error_message=str(e))


def update_account(client, token):
    try:
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            update_data = {
                "username": "updateduser",
                "password": "Updated@1234",
                "mail": "updated@example.com",
                "phone": "0987654321",
                "role": "user"
            }
            response = client.put('/api/account/10', data=json.dumps(update_data), headers=headers, content_type='application/json')
            return add_test_case("Update account details", response, 200)
        return None
    except Exception as e:
        return add_test_case("Update account details", None, 200, error_message=str(e))


def delete_account(client, token):
    try:
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.delete('/api/account/10', headers=headers)
            return add_test_case("Delete an account", response, 200)
        return None
    except Exception as e:
        return add_test_case("Delete an account", None, 200, error_message=str(e))


def create_account_with_missing_field(client):
    try:
        missing_field_data = {
            "username": "incompleteuser"
            # Missing password
        }
        response = client.post('/api/account/', data=json.dumps(missing_field_data), content_type='application/json')
        return add_test_case("Create account with missing required field", response, 400)
    except Exception as e:
        return add_test_case("Create account with missing required field", None, 400, error_message=str(e))


def create_account_with_invalid_json(client):
    try:
        invalid_json = '{"username": "baduser", "password": "badpass"'  # Missing closing }
        response = client.post('/api/account/', data=invalid_json, content_type='application/json')
        return add_test_case("Create account with invalid JSON format", response, 400)
    except Exception as e:
        return add_test_case("Create account with invalid JSON format", None, 400, error_message=str(e))


def sql_injection_test(client):
    try:
        sql_injection_data = {
            "username": "test' OR 1=1; --",
            "password": "password123"
        }
        response = client.post('/api/account/login', data=json.dumps(sql_injection_data), content_type='application/json')
        return add_test_case("SQL Injection attempt during login", response, 401)
    except Exception as e:
        return add_test_case("SQL Injection attempt during login", None, 401, error_message=str(e))


def xss_injection_test(client):
    try:
        xss_data = {
            "username": "<script>alert('XSS');</script>",
            "password": "Test@1234"
        }
        response = client.post('/api/account/', data=json.dumps(xss_data), content_type='application/json')
        return add_test_case("XSS attempt during account creation", response, 400)
    except Exception as e:
        return add_test_case("XSS attempt during account creation", None, 400, error_message=str(e))


def invalid_jwt_token_test(client):
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get('/api/account/', headers=invalid_headers)
        return add_test_case("Access protected route with invalid JWT token", response, 401)
    except Exception as e:
        return add_test_case("Access protected route with invalid JWT token", None, 401, error_message=str(e))


def expired_jwt_token_test(client, token):
    try:
        if token:
            expired_headers = {"Authorization": f"Bearer {token}"}
            response = client.get('/api/account/', headers=expired_headers)
            return add_test_case("Access protected route with expired JWT token", response, 401)
        return None
    except Exception as e:
        return add_test_case("Access protected route with expired JWT token", None, 401, error_message=str(e))


def all_tests(client, token):
    results = []

    # 1. Create Account
    results.append(create_account(client))

    # 2. Duplicate Account Creation
    results.append(duplicate_account_creation(client))

    # 3. Get All Accounts (Without Auth)
    results.append(get_all_accounts_without_auth(client))

    # 4. Login and Get Token
    token = login_and_get_token(client)
    if token:
        # token is valid, so we expect a 200 response with the access token
        results.append(add_test_case("Login to get JWT token", {"access_token": token}, 200))
    else:
        # token is None or invalid, we expect an error response
        results.append(add_test_case("Login to get JWT token", None, 401, error_message="Login failed"))

    # 5. Get All Accounts (With Auth)
    if token:
        results.append(get_all_accounts_with_auth(client, token))

    # 6. Invalid Login
    results.append(invalid_login(client))

    # 7. Update Account
    results.append(update_account(client, token))

    # 8. Delete Account
    results.append(delete_account(client, token))

    # 9. Edge Case - Missing Required Field
    results.append(create_account_with_missing_field(client))

    # 10. Invalid JSON Format
    results.append(create_account_with_invalid_json(client))

    # 11. SQL Injection Test
    results.append(sql_injection_test(client))

    # 12. XSS Injection Test
    results.append(xss_injection_test(client))

    # 13. Invalid JWT Token Test
    results.append(invalid_jwt_token_test(client))

    # 14. Expired JWT Token Test
    results.append(expired_jwt_token_test(client, token))

    return jsonify({"test_results": [result for result in results if result]})
