from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.menutype_controller import create_menutype, get_all_menutypes, get_menutype_by_id, update_menutype, delete_menutype

menutype_bp = Blueprint('menutype', __name__)

# Protected routes (auth required)
menutype_bp.route('/', methods=['POST'])(create_menutype)
menutype_bp.route('/', methods=['GET'])(get_all_menutypes)
menutype_bp.route('/<int:menutype_id>', methods=['GET'])(get_menutype_by_id)
menutype_bp.route('/<int:menutype_id>', methods=['PUT'])(update_menutype)
menutype_bp.route('/<int:menutype_id>', methods=['DELETE'])(delete_menutype)
