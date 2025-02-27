from app.models.ingredients import Ingredients
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

# Create Ingredient
def create_ingredient():
    try:
        data = request.get_json()
        required_keys = ["Ingredients_name"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        Ingredients_name = data["Ingredients_name"]
        Ingredients_image = data.get("Ingredients_image", None)
        Ingredients_des = data.get("Ingredients_des", None)
        main_stock = data.get("main_stock", 0)  # Default 0
        sub_stock = data.get("sub_stock", 0)    # Default 0
        unit = data.get("unit", "unit")

        # Input Validation
        if not isinstance(main_stock, int) or main_stock < 0:
            return jsonify({"message": "main_stock must be a non-negative integer!"}), 400

        if not isinstance(sub_stock, int) or sub_stock < 0:
            return jsonify({"message": "sub_stock must be a non-negative integer!"}), 400

        new_ingredient = Ingredients(
            Ingredients_name=Ingredients_name,
            Ingredients_image=Ingredients_image,
            Ingredients_des=Ingredients_des,
            main_stock=main_stock,
            sub_stock=sub_stock,
            unit=unit
        )
        db.session.add(new_ingredient)
        db.session.commit()

        return jsonify({"message": "Ingredient created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All Ingredients
def get_all_ingredients():
    try:
        ingredients = Ingredients.query.all()
        return jsonify([ingredient.as_dict() for ingredient in ingredients]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get Ingredient by ID
def get_ingredient_by_id(ingredients_id):
    try:
        ingredient = Ingredients.query.get(ingredients_id)
        if ingredient:
            return jsonify(ingredient.as_dict()), 200
        return jsonify({"message": "Ingredient not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update Ingredient
def update_ingredient(ingredients_id):
    try:
        data = request.get_json()
        ingredient = Ingredients.query.get(ingredients_id)

        if ingredient:
            ingredient.Ingredients_name = data.get("Ingredients_name", ingredient.Ingredients_name)
            ingredient.Ingredients_image = data.get("Ingredients_image", ingredient.Ingredients_image)
            ingredient.Ingredients_des = data.get("Ingredients_des", ingredient.Ingredients_des)
            ingredient.main_stock = data.get("main_stock", ingredient.main_stock)
            ingredient.sub_stock = data.get("sub_stock", ingredient.sub_stock)
            ingredient.unit = data.get("unit", ingredient.unit)

            # Input Validation
            if "main_stock" in data and (not isinstance(data["main_stock"], int) or data["main_stock"] < 0):
                return jsonify({"message": "main_stock must be a non-negative integer!"}), 400

            if "sub_stock" in data and (not isinstance(data["sub_stock"], int) or data["sub_stock"] < 0):
                return jsonify({"message": "sub_stock must be a non-negative integer!"}), 400

            db.session.commit()
            return jsonify({"message": "Ingredient updated successfully!"}), 200
        return jsonify({"message": "Ingredient not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete Ingredient
def delete_ingredient(ingredients_id):
    try:
        ingredient = Ingredients.query.get(ingredients_id)
        if ingredient:
            db.session.delete(ingredient)
            db.session.commit()
            return jsonify({"message": "Ingredient deleted successfully!"}), 200
        return jsonify({"message": "Ingredient not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Show/Update Ingredient enable status
def show_ingredient():
    try:
        # รับข้อมูล JSON
        data = request.get_json()
        
        # ตรวจสอบว่า id และ enable ถูกต้อง
        if "id" not in data or "enable" not in data:
            return jsonify({"message": "Both 'id' and 'enable' are required!"}), 400
        
        # ค้นหาวัตถุดิบที่มี Ingredients_id ที่ระบุ
        ingredient = Ingredients.query.get(data["id"])
        if not ingredient:
            return jsonify({"message": "Ingredient not found!"}), 404
        
        # อัปเดตสถานะ enable ของวัตถุดิบ
        enable_value = data["enable"]
        
        # ตรวจสอบว่า enable มีค่าเป็น 0 หรือ 1 เท่านั้น
        if enable_value not in [0, 1]:
            return jsonify({"message": "'enable' must be either 0 or 1!"}), 400

        ingredient.enable = enable_value

        # บันทึกการเปลี่ยนแปลงในฐานข้อมูล
        db.session.commit()

        return jsonify({"message": "Ingredient enable status updated successfully!"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
