from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.menuingredients_controller import (
    create_menu_ingredient,
    get_all_menuingredients,
    get_menu_ingredient_by_id,
    update_menu_ingredient,
    delete_menu_ingredient
)

menuingredients_bp = Blueprint('menuingredients', __name__)

# Protected routes (auth required)
menuingredients_bp.route('/', methods=['POST'])(create_menu_ingredient)
menuingredients_bp.route('/', methods=['GET'])(get_all_menuingredients)
menuingredients_bp.route('/<int:menu_ingredient_id>', methods=['GET'])(get_menu_ingredient_by_id)
menuingredients_bp.route('/<int:menu_ingredient_id>', methods=['PUT'])(update_menu_ingredient)
menuingredients_bp.route('/<int:menu_ingredient_id>', methods=['DELETE'])(delete_menu_ingredient)
