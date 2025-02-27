from app.models.orderitem import OrderItem
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

# Create order item
def create_order_item():
    try:
        data = request.get_json()
        required_keys = ["menu_id", "menu_qty"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            return jsonify({"message": message}), 400

        menu_id = data["menu_id"]
        menu_qty = data["menu_qty"]
        menu_note = data.get("menu_note", None)
        round_order = data.get("round_order", None)
        order_id = data.get("order_id", None)
        status_order = data.get("status_order", None)
        status_serve = data.get("status_serve", None)
        finish_date = data.get("finish_date", None)

        new_order_item = OrderItem(
            menu_id=menu_id,
            menu_qty=menu_qty,
            menu_note=menu_note,
            round_order=round_order,
            order_id=order_id,
            status_order=status_order,
            status_serve=status_serve,
            finish_date=finish_date
        )
        db.session.add(new_order_item)
        db.session.commit()

        return jsonify({"message": "Order item created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All order items
def get_all_order_items():
    try:
        order_items = OrderItem.query.all()
        return jsonify([order_item.as_dict() for order_item in order_items]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get order item by ID
def get_order_item_by_id(order_item_id):
    try:
        order_item = OrderItem.query.get(order_item_id)
        if order_item:
            return jsonify(order_item.as_dict()), 200
        return jsonify({"message": "Order item not found!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update order item
def update_order_item(order_item_id):
    try:
        data = request.get_json()
        order_item = OrderItem.query.get(order_item_id)
        if order_item:
            order_item.menu_id = data.get('menu_id', order_item.menu_id)
            order_item.menu_qty = data.get('menu_qty', order_item.menu_qty)
            order_item.menu_note = data.get('menu_note', order_item.menu_note)
            order_item.round_order = data.get('round_order', order_item.round_order)
            order_item.order_id = data.get('order_id', order_item.order_id)
            order_item.status_order = data.get('status_order', order_item.status_order)
            order_item.status_serve = data.get('status_serve', order_item.status_serve)
            order_item.finish_date = data.get('finish_date', order_item.finish_date)

            db.session.commit()
            return jsonify({"message": "Order item updated successfully!"}), 200
        return jsonify({"message": "Order item not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete order item
def delete_order_item(order_item_id):
    try:
        order_item = OrderItem.query.get(order_item_id)
        if order_item:
            db.session.delete(order_item)
            db.session.commit()
            return jsonify({"message": "Order item deleted successfully!"}), 200
        return jsonify({"message": "Order item not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
