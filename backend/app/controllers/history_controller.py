from app.models.history import History
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Validate Input Function
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create History
def create_history():
    try:
        data = request.get_json()
        required_keys = ["menu_id", "quantity", "total"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        menu_id = data["menu_id"]
        quantity = data["quantity"]
        total = data["total"]
        time_stamp = data.get("time_stamp", datetime.utcnow())

        # Prevent Invalid Data
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"message": "Quantity must be a positive integer!"}), 400

        if not isinstance(total, (int, float)) or total <= 0:
            return jsonify({"message": "Total must be a positive number!"}), 400

        new_history = History(
            menu_id=menu_id,
            quantity=quantity,
            total=total,
            time_stamp=time_stamp
        )
        db.session.add(new_history)
        db.session.commit()

        return jsonify({"message": "History created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All Histories
def get_all_histories():
    try:
        histories = History.query.all()
        return jsonify([history.as_dict() for history in histories]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get History by ID
def get_history_by_id(history_id):
    try:
        history = History.query.get(history_id)
        if history:
            return jsonify(history.as_dict()), 200
        return jsonify({"message": "History not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get Histories by Menu ID
def get_histories_by_menu_id(menu_id):
    try:
        histories = History.query.filter_by(menu_id=menu_id).all()
        if histories:
            return jsonify([history.as_dict() for history in histories]), 200
        return jsonify({"message": "No histories found for this menu_id!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update History
def update_history(history_id):
    try:
        data = request.get_json()
        history = History.query.get(history_id)
        if history:
            history.menu_id = data.get("menu_id", history.menu_id)
            history.quantity = data.get("quantity", history.quantity)
            history.total = data.get("total", history.total)
            history.time_stamp = data.get("time_stamp", history.time_stamp)

            # Prevent Invalid Data
            if "quantity" in data and (not isinstance(data["quantity"], int) or data["quantity"] <= 0):
                return jsonify({"message": "Quantity must be a positive integer!"}), 400

            if "total" in data and (not isinstance(data["total"], (int, float)) or data["total"] <= 0):
                return jsonify({"message": "Total must be a positive number!"}), 400

            db.session.commit()
            return jsonify({"message": "History updated successfully!"}), 200
        return jsonify({"message": "History not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete History
def delete_history(history_id):
    try:
        history = History.query.get(history_id)
        if history:
            db.session.delete(history)
            db.session.commit()
            return jsonify({"message": "History deleted successfully!"}), 200
        return jsonify({"message": "History not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
