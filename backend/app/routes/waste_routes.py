from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.waste_controller import (
    create_waste,
    get_all_wastes,
    get_waste_by_id,
    update_waste,
    delete_waste,
    get_wastes_by_date
)

waste_bp = Blueprint('waste', __name__)

# Protected routes (auth required)
waste_bp.route('/', methods=['POST'])(create_waste)
waste_bp.route('/', methods=['GET'])(get_all_wastes)
waste_bp.route('/<int:waste_id>', methods=['GET'])(get_waste_by_id)
waste_bp.route('/date/<string:waste_date>', methods=['GET'])(get_wastes_by_date)
waste_bp.route('/<int:waste_id>', methods=['PUT'])(update_waste)
waste_bp.route('/<int:waste_id>', methods=['DELETE'])(delete_waste)
