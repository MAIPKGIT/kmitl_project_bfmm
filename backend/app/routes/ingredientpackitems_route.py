from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.ingredientpackitems_controller import (
    create_ingredient_pack_item,
    get_all_ingredient_pack_items,
    get_ingredient_pack_item_by_id,
    update_ingredient_pack_item,
    delete_ingredient_pack_item
)

ingredientpackitems_bp = Blueprint('ingredient_pack_items', __name__)

# Protected routes (auth required)
ingredientpackitems_bp.route('/', methods=['POST'])(create_ingredient_pack_item)
ingredientpackitems_bp.route('/', methods=['GET'])(get_all_ingredient_pack_items)
ingredientpackitems_bp.route('/<int:ingredient_pack_item_id>', methods=['GET'])(get_ingredient_pack_item_by_id)
ingredientpackitems_bp.route('/<int:ingredient_pack_item_id>', methods=['PUT'])(update_ingredient_pack_item)
ingredientpackitems_bp.route('/<int:ingredient_pack_item_id>', methods=['DELETE'])(delete_ingredient_pack_item)
