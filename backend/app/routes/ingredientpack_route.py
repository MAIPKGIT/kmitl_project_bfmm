from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.ingredientpack_controller import (
    create_ingredient_pack,
    get_all_ingredient_packs,
    get_ingredient_pack_by_id,
    update_ingredient_pack,
    delete_ingredient_pack
)

ingredientpack_bp = Blueprint('ingredient_packs', __name__)

# Protected routes (auth required)
ingredientpack_bp.route('/', methods=['POST'])(create_ingredient_pack)
ingredientpack_bp.route('/', methods=['GET'])(get_all_ingredient_packs)
ingredientpack_bp.route('/<int:ingredient_pack_id>', methods=['GET'])(get_ingredient_pack_by_id)
ingredientpack_bp.route('/<int:ingredient_pack_id>', methods=['PUT'])(update_ingredient_pack)
ingredientpack_bp.route('/<int:ingredient_pack_id>', methods=['DELETE'])(delete_ingredient_pack)
