from flask import Blueprint, jsonify, current_app
from app.tests.account_apitest import (
    index,
    all_tests,
    create_account,
    duplicate_account_creation,
    get_all_accounts_without_auth,
    login_and_get_token,
    get_all_accounts_with_auth,
    invalid_login,
    update_account,
    delete_account,
    create_account_with_missing_field,
    create_account_with_invalid_json,
    sql_injection_test,
    xss_injection_test,
    invalid_jwt_token_test,
    expired_jwt_token_test
)

account_apitest_bp = Blueprint('account_test', __name__)

# Route สำหรับทดสอบทั้งหมด
account_apitest_bp.route('/', methods=['GET'])(index)
account_apitest_bp.route('/all_tests', methods=['GET'], endpoint='all_tests')(lambda: all_tests(current_app.test_client(), 'your_token_here'))

# Route สำหรับแต่ละฟังก์ชันทดสอบ
account_apitest_bp.route('/create_account', methods=['GET'], endpoint='create_account_test')(lambda: create_account(current_app.test_client()))
account_apitest_bp.route('/duplicate_account_creation', methods=['GET'], endpoint='duplicate_account_creation_test')(lambda: duplicate_account_creation(current_app.test_client()))
account_apitest_bp.route('/get_all_accounts_without_auth', methods=['GET'], endpoint='get_all_accounts_without_auth_test')(lambda: get_all_accounts_without_auth(current_app.test_client()))
account_apitest_bp.route('/login_and_get_token', methods=['GET'], endpoint='login_and_get_token_test')(lambda: login_and_get_token(current_app.test_client()))
account_apitest_bp.route('/get_all_accounts_with_auth', methods=['GET'], endpoint='get_all_accounts_with_auth_test')(lambda: get_all_accounts_with_auth(current_app.test_client(), 'your_token_here'))
account_apitest_bp.route('/invalid_login', methods=['GET'], endpoint='invalid_login_test')(lambda: invalid_login(current_app.test_client()))
account_apitest_bp.route('/update_account', methods=['GET'], endpoint='update_account_test')(lambda: update_account(current_app.test_client(), 'your_token_here'))
account_apitest_bp.route('/delete_account', methods=['GET'], endpoint='delete_account_test')(lambda: delete_account(current_app.test_client(), 'your_token_here'))
account_apitest_bp.route('/create_account_with_missing_field', methods=['GET'], endpoint='create_account_with_missing_field_test')(lambda: create_account_with_missing_field(current_app.test_client()))
account_apitest_bp.route('/create_account_with_invalid_json', methods=['GET'], endpoint='create_account_with_invalid_json_test')(lambda: create_account_with_invalid_json(current_app.test_client()))
account_apitest_bp.route('/sql_injection_test', methods=['GET'], endpoint='sql_injection_test_test')(lambda: sql_injection_test(current_app.test_client()))
account_apitest_bp.route('/xss_injection_test', methods=['GET'], endpoint='xss_injection_test_test')(lambda: xss_injection_test(current_app.test_client()))
account_apitest_bp.route('/invalid_jwt_token_test', methods=['GET'], endpoint='invalid_jwt_token_test_test')(lambda: invalid_jwt_token_test(current_app.test_client()))
account_apitest_bp.route('/expired_jwt_token_test', methods=['GET'], endpoint='expired_jwt_token_test_test')(lambda: expired_jwt_token_test(current_app.test_client(), 'your_token_here'))
