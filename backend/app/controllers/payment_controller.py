from app import db
from app.models.order import Order
from app.models.orderitem import OrderItem
from app.models.payment import Payment
from app.models.menu import Menu
from app.models.history import History
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from werkzeug.exceptions import BadRequest
from sqlalchemy import text

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
        sanitized_data[key] = str(value).strip()  # Strip any extra spaces or characters
    return sanitized_data

# Create payment
def create_payment():
    try:
        data = request.get_json()
        data = sanitize_input(data)  # Sanitize input data

        required_keys = ["total_price"]
        is_valid, message = validate_input(data, required_keys)

        if not is_valid:
            raise BadRequest(message)

        total_price = data["total_price"]
        payment_method = data.get("payment_method", None)
        payment_status = data.get("payment_status", None)
        payment_date = data.get("payment_date", None)

        new_payment = Payment(
            total_price=total_price,
            payment_method=payment_method,
            payment_status=payment_status,
            payment_date=payment_date
        )
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({"message": "Payment created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except BadRequest as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get All payments
def get_all_payments():
    try:
        payments = Payment.query.all()
        return jsonify([payment.as_dict() for payment in payments]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get payment by ID
def get_payment_by_id(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if payment:
            return jsonify(payment.as_dict()), 200
        return jsonify({"message": "Payment not found!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update payment
def update_payment(payment_id):
    try:
        data = request.get_json()
        data = sanitize_input(data)  # Sanitize input data

        payment = Payment.query.get(payment_id)
        if payment:
            payment.total_price = data.get('total_price', payment.total_price)
            payment.payment_method = data.get('payment_method', payment.payment_method)
            payment.payment_status = data.get('payment_status', payment.payment_status)
            payment.payment_date = data.get('payment_date', payment.payment_date)

            db.session.commit()
            return jsonify({"message": "Payment updated successfully!"}), 200
        return jsonify({"message": "Payment not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except BadRequest as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete payment
def delete_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if payment:
            db.session.delete(payment)
            db.session.commit()
            return jsonify({"message": "Payment deleted successfully!"}), 200
        return jsonify({"message": "Payment not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Function to insert into history table
def insert_history(order_id):
    try:
        # Query to fetch all order items for the given order_id
        order_items = db.session.execute(
            text("SELECT * FROM orderitem WHERE order_id = :order_id"),
            {"order_id": order_id}
        ).mappings().fetchall()

        for item in order_items:
            # Fetch the price of the menu item
            menu_item = Menu.query.get(item['menu_id'])
            if not menu_item:
                continue  # Skip if the menu item doesn't exist

            # Calculate total for the order item
            total = menu_item.price * item['menu_qty']
            
            # Create a new history record
            history_record = History(
                menu_id=item['menu_id'],
                quantity=item['menu_qty'],
                total=total,
                time_stamp=item['finish_date']  # Assuming finish_date is available in orderitem
            )

            # Add the history record to the session
            db.session.add(history_record)

        # Commit the transaction to save all history records
        db.session.commit()

        return True  # Return True if everything went successfully

    except SQLAlchemyError as e:
        db.session.rollback()
        return False, f"Database Error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Unexpected Error: {str(e)}"

# Make payment API
def make_payment():
    try:
        data = request.get_json()

        print("ข้อมูลที่ได้รับจาก Frontend:", data)

        # ตรวจสอบว่ามีข้อมูลครบหรือไม่
        required_keys = ["payment_id", "payment_method"]
        is_valid, message = validate_input(data, required_keys)
        if not is_valid:
            return jsonify({"message": message}), 400

        payment_id = data["payment_id"]
        payment_method = data["payment_method"]

        # ตรวจสอบใน table 'order' เพื่อหาค่า order_id ที่ตรงกับ payment_id
        order = db.session.execute(
            text("SELECT * FROM `order` WHERE payment_id = :payment_id"),
            {"payment_id": payment_id}
        ).mappings().fetchone()

        if not order:
            return jsonify({"message": "Order not found for this payment!"}), 404

        # นำ order_id ไปตรวจสอบใน table 'orderitem' ว่าทุกรายการมี status_order = 2 และ status_serve = 1 หรือไม่
        order_items = db.session.execute(
            text("SELECT * FROM orderitem WHERE order_id = :order_id"),
            {"order_id": order['order_id']}
        ).mappings().fetchall()

        # ตรวจสอบว่าทุกรายการใน orderitem มี status_order = 2 และ status_serve = 1 หรือไม่
        for item in order_items:
            if item['status_order'] != 2 or item['status_serve'] != 1:
                return jsonify({"message": "Cannot proceed, all order items must have status_order = 2 and status_serve = 1!"}), 400

        # เมื่อเงื่อนไขครบถ้วนแล้ว ให้ทำการ Update ข้อมูลใน table 'payment'
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"message": "Payment not found!"}), 404

        payment.payment_method = payment_method
        payment.payment_status = 1  # สถานะการชำระเงินเป็น 1 (สำเร็จ)
        payment.payment_date = datetime.now()  # กำหนดเวลาเป็นปัจจุบัน

        db.session.commit()

        # Insert history after payment is successful
        history_result = insert_history(order['order_id'])

        # ลบข้อมูลที่เกี่ยวข้องใน 'order' และ 'orderitem'
        db.session.execute(
            text("DELETE FROM orderitem WHERE order_id = :order_id"),
            {"order_id": order['order_id']}
        )
        db.session.execute(
            text("DELETE FROM `order` WHERE order_id = :order_id"),
            {"order_id": order['order_id']}
        )
        db.session.commit()

        if history_result is True:
            return jsonify({"message": "Payment and history created successfully!"}), 200
        else:
            return jsonify({"message": history_result[1]}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500


def get_payment_by_table(table_id):
    try:
        # ค้นหา payment_id ที่เชื่อมกับ order ของโต๊ะนี้
        order = Order.query.filter_by(table_id=table_id).first()
        if not order:
            return jsonify({"message": "No order found for this table"}), 404

        payment = Payment.query.get(order.payment_id)
        if not payment:
            return jsonify({"message": "No payment found for this table"}), 404

        return jsonify({
            "payment_id": payment.payment_id,
            "total_price": payment.total_price,
            "payment_method": payment.payment_method,
            "payment_status": payment.payment_status,
            "payment_date": payment.payment_date
        }), 200

    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
