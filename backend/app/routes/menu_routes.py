from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.menu_controller import (
    create_menu,
    get_all_menus,
    get_menu_by_id,
    update_menu,
    delete_menu,
    get_menus_by_type,
    show_mnenu
)

menu_bp = Blueprint('menu', __name__)

# Protected routes (auth required)
menu_bp.route('/', methods=['POST'])(create_menu)
menu_bp.route('/', methods=['GET'])(get_all_menus)
menu_bp.route('/type/<int:type_id>', methods=['GET'])(get_menus_by_type)
menu_bp.route('/<int:menu_id>', methods=['GET'])(get_menu_by_id)
menu_bp.route('/<int:menu_id>', methods=['PUT'])(update_menu)
menu_bp.route('/<int:menu_id>', methods=['DELETE'])(delete_menu)

menu_bp.route('/show_mnenu', methods=['POST'])(show_mnenu)