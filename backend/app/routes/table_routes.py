from flask import Blueprint
from app.middleware.auth_middleware import auth_required
from app.controllers.table_controller import (
    create_table,
    get_all_tables,
    get_table_by_id,
    update_table,
    delete_table,
    get_tables_by_code,
    update_status_table
)

table_bp = Blueprint('table', __name__)

# Protected routes (auth required)
table_bp.route('/', methods=['POST'])(create_table)
table_bp.route('/', methods=['GET'])(get_all_tables)
table_bp.route('/<int:table_id>', methods=['GET'])(get_table_by_id)
table_bp.route('/code/<string:code>', methods=['GET'])(get_tables_by_code)
table_bp.route('/<int:table_id>', methods=['PUT'])(update_table)
table_bp.route('/<int:table_id>', methods=['DELETE'])(delete_table)

table_bp.route('/status', methods=['POST'])(update_status_table)
