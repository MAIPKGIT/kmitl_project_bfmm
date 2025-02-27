from app.models.menutype import MenuType
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create MenuType
def create_menutype():
    try:
        data = request.get_json()
        required_keys = ["name"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        name = data["name"]
        des = data.get("des", None)

        new_menutype = MenuType(name=name, des=des)
        db.session.add(new_menutype)
        db.session.commit()

        return jsonify({"message": "MenuType created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All MenuTypes
def get_all_menutypes():
    try:
        menutypes = MenuType.query.all()
        return jsonify([menutype.as_dict() for menutype in menutypes]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get MenuType by ID
def get_menutype_by_id(menutype_id):
    try:
        menutype = MenuType.query.get(menutype_id)
        if menutype:
            return jsonify(menutype.as_dict()), 200
        return jsonify({"message": "MenuType not found!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update MenuType
def update_menutype(menutype_id):
    try:
        data = request.get_json()
        menutype = MenuType.query.get(menutype_id)
        if menutype:
            menutype.name = data.get('name', menutype.name)
            menutype.des = data.get('des', menutype.des)

            db.session.commit()
            return jsonify({"message": "MenuType updated successfully!"}), 200
        return jsonify({"message": "MenuType not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete MenuType
def delete_menutype(menutype_id):
    try:
        menutype = MenuType.query.get(menutype_id)
        if menutype:
            db.session.delete(menutype)
            db.session.commit()
            return jsonify({"message": "MenuType deleted successfully!"}), 200
        return jsonify({"message": "MenuType not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
