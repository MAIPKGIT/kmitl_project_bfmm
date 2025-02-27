from app.models.menu import Menu
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create menu
def create_menu():
    try:
        data = request.get_json()
        required_keys = ["type_id", "name", "image"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        type_id = data["type_id"]
        name = data["name"]
        image = data["image"]
        des = data.get("des", None)
        price = data.get("price", None)
        tag = data.get("tag", None)
        warning = data.get("warning", None)

        # Additional validation for price
        if price is not None and (not isinstance(price, (int, float)) or price < 0):
            return jsonify({"message": "Price must be a positive number!"}), 400

        new_menu = Menu(
            type_id=type_id,
            name=name,
            image=image,
            des=des,
            price=price,
            tag=tag,
            warning=warning
        )
        db.session.add(new_menu)
        db.session.commit()

        return jsonify({"message": "Menu created successfully!", "menu_id": new_menu.id}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All menus
def get_all_menus():
    try:
        menus = Menu.query.all()
        return jsonify([menu.as_dict() for menu in menus]), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get menu by ID
def get_menu_by_id(menu_id):
    try:
        menu = Menu.query.get(menu_id)
        if menu:
            return jsonify(menu.as_dict()), 200
        return jsonify({"message": "Menu not found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get menus by type_id
def get_menus_by_type(type_id):
    try:
        menus = Menu.query.filter_by(type_id=type_id).all()
        if menus:
            return jsonify([menu.as_dict() for menu in menus]), 200
        return jsonify({"message": "No menus found for this type_id!"}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update menu
def update_menu(menu_id):
    try:
        data = request.get_json()
        menu = Menu.query.get(menu_id)

        if menu:
            menu.type_id = data.get("type_id", menu.type_id)
            menu.name = data.get("name", menu.name)
            menu.image = data.get("image", menu.image)
            menu.des = data.get("des", menu.des)
            menu.price = data.get("price", menu.price)
            menu.tag = data.get("tag", menu.tag)
            menu.warning = data.get("warning", menu.warning)

            # Validation for price
            if "price" in data and (not isinstance(data["price"], (int, float)) or data["price"] < 0):
                return jsonify({"message": "Price must be a positive number!"}), 400

            db.session.commit()
            return jsonify({"message": "Menu updated successfully!"}), 200
        return jsonify({"message": "Menu not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete menu
def delete_menu(menu_id):
    try:
        menu = Menu.query.get(menu_id)
        if menu:
            db.session.delete(menu)
            db.session.commit()
            return jsonify({"message": "Menu deleted successfully!"}), 200
        return jsonify({"message": "Menu not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Change enable status of a menu
def show_mnenu():
    try:
        # รับข้อมูล JSON จาก request
        data = request.get_json()

        # ตรวจสอบว่าในข้อมูลมี 'id' และ 'enable' หรือไม่
        if "id" not in data or "enable" not in data:
            return jsonify({"message": "'id' and 'enable' are required!"}), 400
        
        # ดึงค่า id และ enable จากข้อมูล
        menu_id = data["id"]
        enable_status = data["enable"]

        # ตรวจสอบว่า 'enable' ต้องเป็น 0 หรือ 1 เท่านั้น
        if enable_status not in [0, 1]:
            return jsonify({"message": "'enable' must be either 0 or 1!"}), 400

        # ค้นหาเมนูจากฐานข้อมูลโดยใช้ id
        menu = Menu.query.get(menu_id)

        if menu:
            # อัปเดตค่า enable ในฐานข้อมูล
            menu.enable = enable_status

            # บันทึกการเปลี่ยนแปลงในฐานข้อมูล
            db.session.commit()

            return jsonify({"message": "Menu enable status updated successfully!"}), 200
        else:
            return jsonify({"message": "Menu not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
