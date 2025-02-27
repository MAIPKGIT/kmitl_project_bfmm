from flask import Blueprint, jsonify, request
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