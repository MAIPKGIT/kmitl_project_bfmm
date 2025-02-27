from app.models.menuingredientpack import MenuIngredientPack
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Validate Input Function
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create MenuIngredientPack
def create_menu_ingredient_pack():
    try:
        data = request.get_json()
        required_keys = ["menu_id", "ingredient_pack_id", "qty"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        menu_id = data["menu_id"]
        ingredient_pack_id = data["ingredient_pack_id"]
        qty = data["qty"]

        # Input Validation
        if not isinstance(qty, int) or qty < 0:
            return jsonify({"message": "qty must be a non-negative integer!"}), 400

        new_menu_ingredient_pack = MenuIngredientPack(
            menu_id=menu_id,
            ingredient_pack_id=ingredient_pack_id,
            qty=qty
        )
        db.session.add(new_menu_ingredient_pack)
        db.session.commit()

        return jsonify({"message": "MenuIngredientPack created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All MenuIngredientPacks
def get_all_menu_ingredient_packs():
    try:
        menu_ingredient_packs = MenuIngredientPack.query.all()
        return jsonify([menu_ingredient_pack.as_dict() for menu_ingredient_pack in menu_ingredient_packs]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get MenuIngredientPack by ID
def get_menu_ingredient_pack_by_id(menu_ingredient_pack_id):
    try:
        menu_ingredient_pack = MenuIngredientPack.query.get(menu_ingredient_pack_id)
        if menu_ingredient_pack:
            return jsonify(menu_ingredient_pack.as_dict()), 200
        return jsonify({"message": "MenuIngredientPack not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update MenuIngredientPack
def update_menu_ingredient_pack(menu_ingredient_pack_id):
    try:
        data = request.get_json()
        menu_ingredient_pack = MenuIngredientPack.query.get(menu_ingredient_pack_id)

        if menu_ingredient_pack:
            menu_ingredient_pack.menu_id = data.get("menu_id", menu_ingredient_pack.menu_id)
            menu_ingredient_pack.ingredient_pack_id = data.get("ingredient_pack_id", menu_ingredient_pack.ingredient_pack_id)
            menu_ingredient_pack.qty = data.get("qty", menu_ingredient_pack.qty)

            # Input Validation
            if "qty" in data and (not isinstance(data["qty"], int) or data["qty"] < 0):
                return jsonify({"message": "qty must be a non-negative integer!"}), 400

            db.session.commit()
            return jsonify({"message": "MenuIngredientPack updated successfully!"}), 200
        return jsonify({"message": "MenuIngredientPack not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete MenuIngredientPack
def delete_menu_ingredient_pack(menu_ingredient_pack_id):
    try:
        menu_ingredient_pack = MenuIngredientPack.query.get(menu_ingredient_pack_id)
        if menu_ingredient_pack:
            db.session.delete(menu_ingredient_pack)
            db.session.commit()
            return jsonify({"message": "MenuIngredientPack deleted successfully!"}), 200
        return jsonify({"message": "MenuIngredientPack not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
