from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.menuingredientpack_controller import (
    create_menu_ingredient_pack,
    get_all_menu_ingredient_packs,
    get_menu_ingredient_pack_by_id,
    update_menu_ingredient_pack,
    delete_menu_ingredient_pack
)

menuingredientpack_bp = Blueprint('menu_ingredient_packs', __name__)

# Protected routes (auth required)
menuingredientpack_bp.route('/', methods=['POST'])(create_menu_ingredient_pack)
menuingredientpack_bp.route('/', methods=['GET'])(get_all_menu_ingredient_packs)
menuingredientpack_bp.route('/<int:menu_ingredient_pack_id>', methods=['GET'])(get_menu_ingredient_pack_by_id)
menuingredientpack_bp.route('/<int:menu_ingredient_pack_id>', methods=['PUT'])(update_menu_ingredient_pack)
menuingredientpack_bp.route('/<int:menu_ingredient_pack_id>', methods=['DELETE'])(delete_menu_ingredient_pack)
