from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.account_controller import (
    create_account,
    get_all_accounts,
    get_account_by_id,
    update_account,
    delete_account,
    login,
    logout
)

account_bp = Blueprint('account', __name__)

# Public routes
account_bp.route('/login', methods=['POST'])(login)
account_bp.route('/logout', methods=['POST'])(logout)

account_bp.route('/', methods=['POST'])(create_account)
account_bp.route('/', methods=['GET'])(get_all_accounts)
account_bp.route('/<int:account_id>', methods=['GET'])(get_account_by_id)
account_bp.route('/<int:account_id>', methods=['PUT'])(update_account)
account_bp.route('/<int:account_id>', methods=['DELETE'])(delete_account)