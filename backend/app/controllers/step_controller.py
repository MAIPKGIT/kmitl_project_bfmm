from app.models.step import Step
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Utility function to sanitize input
def sanitize_input(data):
    sanitized_data = {}
    for key, value in data.items():
        if value:  # Only sanitize non-empty values
            sanitized_data[key] = str(value).strip()  # Strip any extra spaces or characters
    return sanitized_data

# Create step
def create_step():
    try:
        data = request.get_json()
        data = sanitize_input(data)  # Sanitize input data

        required_keys = ["step", "menu_id"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            raise BadRequest(message)

        step = data["step"]
        menu_id = data["menu_id"]
        description = data.get("description", None)

        new_step = Step(step=step, menu_id=menu_id, description=description)
        db.session.add(new_step)
        db.session.commit()

        return jsonify({"message": "Step created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except BadRequest as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All steps
def get_all_steps():
    try:
        steps = Step.query.all()
        return jsonify([step.as_dict() for step in steps]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get step by ID
def get_step_by_id(step_id):
    try:
        step = Step.query.get(step_id)
        if step:
            return jsonify(step.as_dict()), 200
        return jsonify({"message": "Step not found!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get steps by menu_id
def get_steps_by_menu_id(menu_id):
    try:
        steps = Step.query.filter_by(menu_id=menu_id).all()
        if steps:
            return jsonify([step.as_dict() for step in steps]), 200
        return jsonify({"message": "No steps found for this menu_id!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update step
def update_step(step_id):
    try:
        data = request.get_json()
        data = sanitize_input(data)  # Sanitize input data

        step = Step.query.get(step_id)
        if step:
            step.step = data.get('step', step.step)
            step.description = data.get('description', step.description)
            step.menu_id = data.get('menu_id', step.menu_id)

            db.session.commit()
            return jsonify({"message": "Step updated successfully!"}), 200
        return jsonify({"message": "Step not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except BadRequest as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete step
def delete_step(step_id):
    try:
        step = Step.query.get(step_id)
        if step:
            db.session.delete(step)
            db.session.commit()
            return jsonify({"message": "Step deleted successfully!"}), 200
        return jsonify({"message": "Step not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
