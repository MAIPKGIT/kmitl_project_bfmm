from app.models.menuingredients import MenuIngredients
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create menu ingredient
def create_menu_ingredient():
    try:
        data = request.get_json()
        required_keys = ["menu_id", "ingredient_id"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        menu_id = data["menu_id"]
        ingredient_id = data["ingredient_id"]
        volume = data.get("volume", None)
        unit = data.get("unit", None)

        # Validate volume (must be positive if provided)
        if volume is not None and (not isinstance(volume, (int, float)) or volume < 0):
            return jsonify({"message": "Volume must be a positive number!"}), 400

        new_menu_ingredient = MenuIngredients(
            menu_id=menu_id,
            ingredient_id=ingredient_id,
            volume=volume,
            unit=unit
        )
        db.session.add(new_menu_ingredient)
        db.session.commit()

        return jsonify({"message": "MenuIngredient created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All menu ingredients
def get_all_menuingredients():
    try:
        menuingredients = MenuIngredients.query.all()
        return jsonify([menu_ingredient.as_dict() for menu_ingredient in menuingredients]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get menu ingredient by ID
def get_menu_ingredient_by_id(menu_ingredient_id):
    try:
        menu_ingredient = MenuIngredients.query.get(menu_ingredient_id)
        if menu_ingredient:
            return jsonify(menu_ingredient.as_dict()), 200
        return jsonify({"message": "MenuIngredient not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update menu ingredient
def update_menu_ingredient(menu_ingredient_id):
    try:
        data = request.get_json()
        menu_ingredient = MenuIngredients.query.get(menu_ingredient_id)

        if menu_ingredient:
            menu_ingredient.menu_id = data.get('menu_id', menu_ingredient.menu_id)
            menu_ingredient.ingredient_id = data.get('ingredient_id', menu_ingredient.ingredient_id)
            menu_ingredient.volume = data.get('volume', menu_ingredient.volume)
            menu_ingredient.unit = data.get('unit', menu_ingredient.unit)

            # Validate volume (must be positive if provided)
            if "volume" in data and (not isinstance(data["volume"], (int, float)) or data["volume"] < 0):
                return jsonify({"message": "Volume must be a positive number!"}), 400

            db.session.commit()
            return jsonify({"message": "MenuIngredient updated successfully!"}), 200
        return jsonify({"message": "MenuIngredient not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete menu ingredient
def delete_menu_ingredient(menu_ingredient_id):
    try:
        menu_ingredient = MenuIngredients.query.get(menu_ingredient_id)
        if menu_ingredient:
            db.session.delete(menu_ingredient)
            db.session.commit()
            return jsonify({"message": "MenuIngredient deleted successfully!"}), 200
        return jsonify({"message": "MenuIngredient not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
