from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.step_controller import (
    create_step,
    get_all_steps,
    get_step_by_id,
    update_step,
    delete_step,
    get_steps_by_menu_id
)

step_bp = Blueprint('step', __name__)

# Protected routes (auth required)
step_bp.route('/', methods=['POST'])(create_step)
step_bp.route('/', methods=['GET'])(get_all_steps)
step_bp.route('/<int:step_id>', methods=['GET'])(get_step_by_id)
step_bp.route('/menu/<int:menu_id>', methods=['GET'])(get_steps_by_menu_id)
step_bp.route('/<int:step_id>', methods=['PUT'])(update_step)
step_bp.route('/<int:step_id>', methods=['DELETE'])(delete_step)
