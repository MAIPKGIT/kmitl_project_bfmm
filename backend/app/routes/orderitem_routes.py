from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.orderitem_controller import (
    create_order_item,
    get_all_order_items,
    get_order_item_by_id,
    update_order_item,
    delete_order_item
)

orderitem_bp = Blueprint('orderitem', __name__)

# Protected routes (auth required)
orderitem_bp.route('/', methods=['POST'])(create_order_item)
orderitem_bp.route('/', methods=['GET'])(get_all_order_items)
orderitem_bp.route('/<int:order_item_id>', methods=['GET'])(get_order_item_by_id)
orderitem_bp.route('/<int:order_item_id>', methods=['PUT'])(update_order_item)
orderitem_bp.route('/<int:order_item_id>', methods=['DELETE'])(delete_order_item)
