from app.models.ingredientpack import IngredientPack
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Validate Input Function
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create IngredientPack
def create_ingredient_pack():
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

        new_ingredient_pack = IngredientPack(
            menu_id=menu_id,
            ingredient_pack_id=ingredient_pack_id,
            qty=qty
        )
        db.session.add(new_ingredient_pack)
        db.session.commit()

        return jsonify({"message": "IngredientPack created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All IngredientPacks
def get_all_ingredient_packs():
    try:
        ingredient_packs = IngredientPack.query.all()
        return jsonify([ingredient_pack.as_dict() for ingredient_pack in ingredient_packs]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get IngredientPack by ID
def get_ingredient_pack_by_id(ingredient_pack_id):
    try:
        ingredient_pack = IngredientPack.query.get(ingredient_pack_id)
        if ingredient_pack:
            return jsonify(ingredient_pack.as_dict()), 200
        return jsonify({"message": "IngredientPack not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update IngredientPack
def update_ingredient_pack(ingredient_pack_id):
    try:
        data = request.get_json()
        ingredient_pack = IngredientPack.query.get(ingredient_pack_id)

        if ingredient_pack:
            ingredient_pack.menu_id = data.get("menu_id", ingredient_pack.menu_id)
            ingredient_pack.ingredient_pack_id = data.get("ingredient_pack_id", ingredient_pack.ingredient_pack_id)
            ingredient_pack.qty = data.get("qty", ingredient_pack.qty)

            # Input Validation
            if "qty" in data and (not isinstance(data["qty"], int) or data["qty"] < 0):
                return jsonify({"message": "qty must be a non-negative integer!"}), 400

            db.session.commit()
            return jsonify({"message": "IngredientPack updated successfully!"}), 200
        return jsonify({"message": "IngredientPack not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete IngredientPack
def delete_ingredient_pack(ingredient_pack_id):
    try:
        ingredient_pack = IngredientPack.query.get(ingredient_pack_id)
        if ingredient_pack:
            db.session.delete(ingredient_pack)
            db.session.commit()
            return jsonify({"message": "IngredientPack deleted successfully!"}), 200
        return jsonify({"message": "IngredientPack not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
