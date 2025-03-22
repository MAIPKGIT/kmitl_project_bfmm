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
        required_keys = ["name", "description", "stock"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        name = data["name"]
        description = data["description"]
        stock = data["stock"]

        # Validate stock
        if not isinstance(stock, int) or stock < 0:
            return jsonify({"message": "stock must be a non-negative integer!"}), 400

        new_ingredient_pack = IngredientPack(
            name=name,
            description=description,
            stock=stock
        )
        db.session.add(new_ingredient_pack)
        db.session.commit()

        return jsonify({
            "message": "IngredientPack created successfully!",
            "id": new_ingredient_pack.id 
        }), 201

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
            if "stock" in data:
                if not isinstance(data["stock"], int) or data["stock"] < 0:
                    return jsonify({"message": "stock must be a non-negative integer!"}), 400

            ingredient_pack.name = data.get("name", ingredient_pack.name)
            ingredient_pack.description = data.get("description", ingredient_pack.description)
            ingredient_pack.stock = data.get("stock", ingredient_pack.stock)

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