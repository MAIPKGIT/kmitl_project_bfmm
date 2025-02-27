from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.ingredients_controller import (
    create_ingredient,
    get_all_ingredients,
    get_ingredient_by_id,
    update_ingredient,
    delete_ingredient,
    show_ingredient
)

ingredients_bp = Blueprint('ingredients', __name__)

# Protected routes (auth required)
ingredients_bp.route('/', methods=['POST'])(create_ingredient)
ingredients_bp.route('/', methods=['GET'])(get_all_ingredients)
ingredients_bp.route('/<int:ingredients_id>', methods=['GET'])(get_ingredient_by_id)
ingredients_bp.route('/<int:ingredients_id>', methods=['PUT'])(update_ingredient)
ingredients_bp.route('/<int:ingredients_id>', methods=['DELETE'])(delete_ingredient)

ingredients_bp.route('/show_ingredient', methods=['POST'])(show_ingredient)