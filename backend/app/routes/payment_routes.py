from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.payment_controller import (
    create_payment,
    get_all_payments,
    get_payment_by_id,
    update_payment,
    delete_payment,
    make_payment,
    get_payment_by_table
)

payment_bp = Blueprint('payment', __name__)

# Protected routes (auth required)
payment_bp.route('/', methods=['POST'])(create_payment)
payment_bp.route('/', methods=['GET'])(get_all_payments)
payment_bp.route('/<int:payment_id>', methods=['GET'])(get_payment_by_id)
payment_bp.route('/<int:payment_id>', methods=['PUT'])(update_payment)
payment_bp.route('/<int:payment_id>', methods=['DELETE'])(delete_payment)

payment_bp.route('/make_payment', methods=['POST'])(make_payment)
payment_bp.route('/table/<int:table_id>', methods=['GET'])(get_payment_by_table)
