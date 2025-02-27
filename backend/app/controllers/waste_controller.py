from app.models.waste import Waste
from app import db
from flask import jsonify, request
from datetime import datetime
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

# Create waste
def create_waste():
    try:
        data = request.get_json()
        data = sanitize_input(data)  # Sanitize input data

        required_keys = ["item_name", "quantity"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            raise BadRequest(message)

        item_name = data["item_name"]
        quantity = data["quantity"]
        unit = data.get("unit", None)
        price = data.get("price", None)
        waste_date = data.get("waste_date", None)
        reason = data.get("reason", None)
        note = data.get("note", None)

        new_waste = Waste(
            item_name=item_name,
            quantity=quantity,
            unit=unit,
            price=price,
            waste_date=waste_date,
            reason=reason,
            note=note
        )
        db.session.add(new_waste)
        db.session.commit()

        return jsonify({"message": "Waste record created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except BadRequest as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All wastes
def get_all_wastes():
    try:
        wastes = Waste.query.all()
        return jsonify([waste.as_dict() for waste in wastes]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get waste by ID
def get_waste_by_id(waste_id):
    try:
        waste = Waste.query.get(waste_id)
        if waste:
            return jsonify(waste.as_dict()), 200
        return jsonify({"message": "Waste record not found!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get wastes by date
def get_wastes_by_date(waste_date):
    try:
        parsed_date = datetime.strptime(waste_date, "%Y-%m-%d")
        wastes = Waste.query.filter(db.func.date(Waste.waste_date) == parsed_date.date()).all()
        if wastes:
            return jsonify([waste.as_dict() for waste in wastes]), 200
        return jsonify({"message": "No waste records found for this date!"}), 404
    except ValueError:
        return jsonify({"message": "Invalid date format! Use YYYY-MM-DD."}), 400
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update waste
def update_waste(waste_id):
    try:
        data = request.get_json()
        data = sanitize_input(data)  # Sanitize input data

        waste = Waste.query.get(waste_id)
        if waste:
            waste.item_name = data.get('item_name', waste.item_name)
            waste.quantity = data.get('quantity', waste.quantity)
            waste.unit = data.get('unit', waste.unit)
            waste.price = data.get('price', waste.price)
            waste.waste_date = data.get('waste_date', waste.waste_date)
            waste.reason = data.get('reason', waste.reason)
            waste.note = data.get('note', waste.note)

            db.session.commit()
            return jsonify({"message": "Waste record updated successfully!"}), 200
        return jsonify({"message": "Waste record not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except BadRequest as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete waste
def delete_waste(waste_id):
    try:
        waste = Waste.query.get(waste_id)
        if waste:
            db.session.delete(waste)
            db.session.commit()
            return jsonify({"message": "Waste record deleted successfully!"}), 200
        return jsonify({"message": "Waste record not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
