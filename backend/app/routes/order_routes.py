from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.order_controller import (
    create_order,
    get_all_orders,
    get_all_now,
    get_order_by_id,
    update_order,
    delete_order,
    change_status_order,
    change_status_serve,
    cancel_order,
    waste_order,
    stock_manager,
    get_orderitem_by_table
)

order_bp = Blueprint('order', __name__)

# Protected routes (auth required)
order_bp.route('/', methods=['POST'])(create_order)
order_bp.route('/', methods=['GET'])(get_all_orders)
order_bp.route('/get_all_now', methods=['GET'])(get_all_now)
order_bp.route('/<int:order_id>', methods=['GET'])(get_order_by_id)
order_bp.route('/<int:order_id>', methods=['PUT'])(update_order)
order_bp.route('/<int:order_id>', methods=['DELETE'])(delete_order)
order_bp.route('/get_orderitem_by_table/<int:table_id>', methods=['GET'])(get_orderitem_by_table)
order_bp.route('/stock_manager', methods=['POST'])(stock_manager)
order_bp.route('/change_status_order', methods=['POST'])(change_status_order)
order_bp.route('/change_status_serve', methods=['POST'])(change_status_serve)
order_bp.route('/cancel_order', methods=['POST'])(cancel_order)
order_bp.route('/waste_order', methods=['POST'])(waste_order)
