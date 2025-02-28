from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.history_controller import (
    create_history,
    get_all_histories,
    get_history_by_id,
    update_history,
    delete_history,
    get_histories_by_menu_id,
    get_histories_by_date
)

history_bp = Blueprint('history', __name__)

# Protected routes (auth required)
history_bp.route('/', methods=['POST'])(auth_required(create_history))
history_bp.route('/', methods=['GET'])(get_all_histories)
history_bp.route('/<int:history_id>', methods=['GET'])(get_history_by_id)
history_bp.route('/menu/<int:menu_id>', methods=['GET'])(get_histories_by_menu_id)
history_bp.route('/<int:history_id>', methods=['PUT'])(update_history)
history_bp.route('/<int:history_id>', methods=['DELETE'])(delete_history)
history_bp.route('/date/<string:history_date>', methods=['GET'])(get_histories_by_date)