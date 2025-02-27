from app.models.order import Order
from app import db
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from datetime import datetime
from app.models.orderitem import OrderItem
from app.models.menu import Menu
from app.models.payment import Payment
from app.models.table import Table
from app.models.ingredients import Ingredients
from app.models.waste import Waste

from app.models.menuingredients import MenuIngredients
from app.models.menuingredientpack import MenuIngredientPack
from app.models.ingredientpackitems import IngredientPackItems
from sqlalchemy.exc import SQLAlchemyError

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

def stock_manager():
    try:
        # รับข้อมูล JSON จาก API
        data = request.get_json()
        menu_id = data.get("menu_id")
        qty = data.get("qty")

        # ตรวจสอบข้อมูลที่ได้รับมา
        if not menu_id or not qty:
            return jsonify({"message": "'menu_id' and 'qty' are required!"}), 400

        # 1. ค้นหาข้อมูลจาก table 'menuingredients' และตัด stock จาก 'ingredients'
        menu_ingredients = db.session.execute(
            text("SELECT ingredient_id, volume FROM menuingredients WHERE menu_id = :menu_id"),
            {"menu_id": menu_id}
        ).mappings().fetchall()

        ingredient_ids = [ingredient["ingredient_id"] for ingredient in menu_ingredients]

        if ingredient_ids:
            ingredient_stocks = db.session.execute(
                text(f"SELECT Ingredients_id, main_stock FROM ingredients WHERE Ingredients_id IN ({', '.join(map(str, ingredient_ids))})")
            ).mappings().fetchall()
        else:
            ingredient_stocks = []

        stock_dict = {item["Ingredients_id"]: item["main_stock"] for item in ingredient_stocks}

        for ingredient in menu_ingredients:
            ingredient_id = ingredient["ingredient_id"]
            volume = ingredient["volume"]

            if ingredient_id in stock_dict:
                new_stock = stock_dict[ingredient_id] - (volume * qty)

                db.session.execute(
                    text("UPDATE ingredients SET main_stock = :new_stock WHERE Ingredients_id = :ingredient_id"),
                    {"new_stock": new_stock, "ingredient_id": ingredient_id}
                )
            else:
                return jsonify({"message": f"Ingredient with id {ingredient_id} not found!"}), 404

        # 2. ค้นหาข้อมูลจาก table 'menuingredientpack' และตัด stock จาก 'ingredientpack'
        menu_ingredient_packs = db.session.execute(
            text("SELECT ingredient_pack_id, qty FROM menuingredientpack WHERE menu_id = :menu_id"),
            {"menu_id": menu_id}
        ).mappings().fetchall()

        ingredient_pack_ids = [ingredient_pack["ingredient_pack_id"] for ingredient_pack in menu_ingredient_packs]

        if ingredient_pack_ids:
            ingredient_pack_stocks = db.session.execute(
                text(f"SELECT id, stock FROM ingredientpack WHERE id IN ({', '.join(map(str, ingredient_pack_ids))})")
            ).mappings().fetchall()
        else:
            ingredient_pack_stocks = []

        pack_stock_dict = {item["id"]: item["stock"] for item in ingredient_pack_stocks}

        for ingredient_pack in menu_ingredient_packs:
            ingredient_pack_id = ingredient_pack["ingredient_pack_id"]
            pack_qty = ingredient_pack["qty"]

            if ingredient_pack_id in pack_stock_dict:
                new_stock = pack_stock_dict[ingredient_pack_id] - (pack_qty * qty)

                db.session.execute(
                    text("UPDATE ingredientpack SET stock = :new_stock WHERE id = :pack_id"),
                    {"new_stock": new_stock, "pack_id": ingredient_pack_id}
                )
            else:
                return jsonify({"message": f"Ingredient Pack with id {ingredient_pack_id} not found!"}), 404

        db.session.commit()
        return jsonify({"message": "Stock has been successfully updated!"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Create order
def create_order():
    try:
        data = request.get_json()

        table_id = data.get('table')
        code_from_api = data.get('code')

        if not table_id:
            raise ValueError("'table' is required!")

        # ตรวจสอบว่า table_id ตรงและสถานะเป็น 'enable'
        table = db.session.execute(
            text("SELECT * FROM `table` WHERE table_id = :table_id AND status = 'enable'"),
            {"table_id": table_id}
        ).mappings().fetchone()

        if not table:
            return jsonify({"message": "Table is not available or disabled!"}), 400

        # ตรวจสอบว่า code ตรงกับที่เก็บใน table หรือไม่
        if table["code"] != code_from_api:
            return jsonify({"message": "Code does not match!"}), 400

        # ค้นหา payment ที่ยังไม่ชำระ (payment_status = 0) สำหรับโต๊ะนี้
        unpaid_payment = db.session.execute(
            text("SELECT * FROM payment WHERE payment_id IN "
                 "(SELECT payment_id FROM `order` WHERE table_id = :table_id) "
                 "AND payment_status = 0"),
            {"table_id": table_id}
        ).mappings().fetchone()

        if unpaid_payment:
            # ถ้ามี payment ที่ยังไม่ชำระ → อัปเดตราคายอดรวม
            total_price = data["total_price"] + unpaid_payment["total_price"]
            db.session.execute(
                text("UPDATE payment SET total_price = :total_price WHERE payment_id = :payment_id"),
                {"total_price": total_price, "payment_id": unpaid_payment["payment_id"]}
            )

            new_order = Order(
                payment_id=unpaid_payment["payment_id"], 
                table_id=table_id,
                create_order=datetime.now(),
                number_of_people=data["people"]
            )
            db.session.add(new_order)
            db.session.commit()

            create_date = datetime.now()

            for item in data["items"]:
                new_orderitem = OrderItem(
                    order_id=new_order.order_id, 
                    menu_id=item["id"],
                    menu_qty=item["qty"],
                    menu_note=item["note"],
                    round_order=1, 
                    status_order=0,
                    status_serve=0
                )
                db.session.add(new_orderitem)

            db.session.commit()
            return jsonify({"message": "New order created under the same payment!"}), 201

        # ถ้าไม่มี payment ที่ยังไม่ชำระ → สร้าง payment และ order ใหม่
        new_payment = Payment(
            total_price=data["total_price"],
            payment_method=data.get("payment_method", None),
            payment_status=0,
            payment_date=data.get("payment_date", None)
        )
        db.session.add(new_payment)
        db.session.commit()

        new_order = Order(
            payment_id=new_payment.payment_id,
            table_id=table_id,
            create_order=datetime.now(),
            number_of_people=data["people"]
        )
        db.session.add(new_order)
        db.session.commit()

        for item in data["items"]:
            new_orderitem = OrderItem(
                order_id=new_order.order_id,
                menu_id=item["id"],
                menu_qty=item["qty"],
                menu_note=item["note"],
                round_order=1,
                status_order=0,
                status_serve=0
            )
            db.session.add(new_orderitem)

        db.session.commit()
        return jsonify({"message": "New order and payment created!"}), 201

    except ValueError as ve:
        return jsonify({"message": f"Input Error: {str(ve)}"}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

def get_all_now():
    try:
        # ดึงข้อมูล orders พร้อมกับข้อมูลจาก orderitem และ menu โดยกรองเฉพาะ status_serve = 0
        query = """
            SELECT o.order_id, oi.order_item_id, o.table_id, oi.round_order, oi.create_date, 
                m.id AS menu_id, m.name AS menu_name, m.price, oi.menu_qty, oi.menu_note,
                m.type_id AS menu_type_id, oi.status_serve
            FROM `order` o
            LEFT JOIN orderitem oi ON o.order_id = oi.order_id
            LEFT JOIN menu m ON oi.menu_id = m.id
            WHERE oi.status_serve = 0 
            ORDER BY o.order_id, oi.round_order, oi.create_date
        """

        # ใช้ mappings() เพื่อแปลงผลลัพธ์เป็น dict
        result = db.session.execute(text(query)).mappings().fetchall()

        # แปลงผลลัพธ์ให้เป็น dictionary
        result_dict = []
        for row in result:
            row_dict = dict(row)  # แปลงแต่ละ row เป็น dictionary
            result_dict.append(row_dict)

        # เตรียมตัวแปรสำหรับเก็บข้อมูล
        orders_dict = {}

        for row in result_dict:
            order_id = row['order_id']
            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    'order_id': order_id,
                    'table_id': row['table_id'],
                    'orders_items': []
                }

            # ตรวจสอบว่า round_order และ create_date ถูกต้องหรือไม่
            round_order = row['round_order']
            create_date = row['create_date'].strftime('%d/%m/%Y %H:%M')

            # สร้างข้อมูลในรูปแบบที่ต้องการ
            order_item = {
                'order_item_id': row['order_item_id'],
                'round': round_order,
                'create_date': create_date,
                'menus': [
                    {
                        'menu_id': row['menu_id'],
                        'menu_name': row['menu_name'],
                        'menu_type_id': row['menu_type_id'],
                        'price': row['price'],
                        'menu_qty': row['menu_qty'],
                        'menu_note': row['menu_note'],
                        'total': row['price'] * row['menu_qty']
                    }
                ]
            }

            # เพิ่มข้อมูลเมนูในรายการของ order_item
            orders_dict[order_id]['orders_items'].append(order_item)

        # คำนวณยอดรวมสำหรับแต่ละออร์เดอร์
        for order in orders_dict.values():
            total = sum(item['menus'][0]['total'] for item in order['orders_items'])
            order['total'] = total

        return jsonify(orders_dict), 200

    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
    
# Get All orders
def get_all_orders():
    try:
        orders = Order.query.all()
        return jsonify([order.as_dict() for order in orders]), 200
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Get order by ID
def get_order_by_id(order_id):
    try:
        order = Order.query.get(order_id)
        if order:
            return jsonify(order.as_dict()), 200
        return jsonify({"message": "Order not found!"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Update order
def update_order(order_id):
    try:
        data = request.get_json()
        order = Order.query.get(order_id)
        if order:
            order.payment_id = data.get('payment_id', order.payment_id)
            order.table_id = data.get('table_id', order.table_id)
            order.number_of_people = data.get('number_of_people', order.number_of_people)

            db.session.commit()
            return jsonify({"message": "Order updated successfully!"}), 200
        return jsonify({"message": "Order not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Delete order
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return jsonify({"message": "Order deleted successfully!"}), 200
        return jsonify({"message": "Order not found!"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Function to change the status of serve
def change_status_serve():
    try:
        data = request.get_json()

        # ตรวจสอบว่าค่า input ครบหรือไม่
        required_keys = ['order', 'order_item', 'operation']
        valid, message = validate_input(data, required_keys)
        if not valid:
            return jsonify({"message": message}), 400

        order_id = data['order']
        order_item_id = data['order_item']
        operation = data['operation']

        # ตรวจสอบว่า order_id และ order_item_id เป็นตัวเลขที่ถูกต้อง
        if not isinstance(order_id, int) or not isinstance(order_item_id, int):
            return jsonify({"message": "'order' and 'order_item' must be integers!"}), 400

        if operation not in ['next', 'back']:
            return jsonify({"message": "'operation' must be either 'next' or 'back'!"}), 400

        # ตรวจสอบข้อมูล order
        order = db.session.execute(
            text("SELECT * FROM `order` WHERE order_id = :order_id"),
            {"order_id": str(order_id)}
        ).mappings().fetchone()

        if not order:
            return jsonify({"message": "Order not found!"}), 404

        # ตรวจสอบสถานะการชำระเงิน
        payment = db.session.execute(
            text("SELECT * FROM payment WHERE payment_id = :payment_id"),
            {"payment_id": order['payment_id']}
        ).mappings().fetchone()

        if payment and payment['payment_status'] == 1:
            return jsonify({"message": "Payment is completed, no further action required!"}), 400

        # ตรวจสอบข้อมูล order_item
        order_item = db.session.execute(
            text("SELECT * FROM orderitem WHERE order_item_id = :order_item_id"),
            {"order_item_id": str(order_item_id)}
        ).mappings().fetchone()

        if not order_item:
            return jsonify({"message": "Order item not found!"}), 404

        current_status = order_item['status_order']

        # เช็คว่า status_order เป็น 2 หรือไม่ก่อนจะเปลี่ยน status_serve
        if current_status == 2:
            current_serve_status = order_item['status_serve']

            # เช็คเงื่อนไขการวนค่าของ status_serve
            if operation == 'next':
                new_status = 0 if current_serve_status == 1 else 1
            elif operation == 'back':
                new_status = 1 if current_serve_status == 0 else 0
            else:
                return jsonify({"message": "Invalid operation!"}), 400

            db.session.execute(
                text("UPDATE orderitem SET status_serve = :new_status WHERE order_item_id = :order_item_id"),
                {"new_status": new_status, "order_item_id": str(order_item_id)}
            )
            db.session.commit()
            return jsonify({"message": "Status of serve updated!", "new_status": new_status}), 200
        else:
            return jsonify({"message": "Cannot change status_serve unless status_order is 2!"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500


def change_status_order():
    try:
        data = request.get_json()

        # ตรวจสอบว่าค่า input ครบหรือไม่
        required_keys = ['order', 'order_item', 'operation']
        valid, message = validate_input(data, required_keys)
        if not valid:
            return jsonify({"message": message}), 400

        order_id = data['order']
        order_item_id = data['order_item']
        operation = data['operation']

        # ตรวจสอบว่า order_id และ order_item_id เป็นตัวเลขที่ถูกต้อง
        if not isinstance(order_id, int) or not isinstance(order_item_id, int):
            return jsonify({"message": "'order' and 'order_item' must be integers!"}), 400

        if operation not in ['next', 'back']:
            return jsonify({"message": "'operation' must be either 'next' or 'back'!"}), 400

        # ตรวจสอบข้อมูล order
        order = db.session.execute(
            text("SELECT * FROM `order` WHERE order_id = :order_id"),
            {"order_id": str(order_id)}
        ).mappings().fetchone()

        if not order:
            return jsonify({"message": "Order not found!"}), 404

        # ตรวจสอบสถานะการชำระเงิน
        payment = db.session.execute(
            text("SELECT * FROM payment WHERE payment_id = :payment_id"),
            {"payment_id": order['payment_id']}
        ).mappings().fetchone()

        if payment and payment['payment_status'] == 1:
            return jsonify({"message": "Payment is completed, no further action required!"}), 400

        # ตรวจสอบข้อมูล order_item
        order_item = db.session.execute(
            text("SELECT * FROM orderitem WHERE order_item_id = :order_item_id"),
            {"order_item_id": str(order_item_id)}
        ).mappings().fetchone()

        if not order_item:
            return jsonify({"message": "Order item not found!"}), 404

        current_status = order_item['status_order']
        current_serve_status = order_item['status_serve']

        # เช็คเงื่อนไขการเปลี่ยน status_order
        if operation == 'next':
            new_status = 0 if current_status == 2 else current_status + 1
        elif operation == 'back':
            new_status = 2 if current_status == 0 else current_status - 1
        else:
            return jsonify({"message": "Invalid operation!"}), 400

        # ตรวจสอบก่อนการอัพเดทว่า status_order ไม่ใช่ 2
        if new_status != 2:
            # ถ้าไม่ใช่ค่า 2 ให้ทำการอัปเดต status_order แล้วปรับ status_serve กลับเป็น 0
            db.session.execute(
                text("UPDATE orderitem SET status_order = :new_status WHERE order_item_id = :order_item_id"),
                {"new_status": new_status, "order_item_id": str(order_item_id)}
            )
            if current_serve_status == 1:
                db.session.execute(
                    text("UPDATE orderitem SET status_serve = 0 WHERE order_item_id = :order_item_id"),
                    {"order_item_id": str(order_item_id)}
                )
        else:
            # ถ้า new_status เป็น 2 ก็อัปเดตเฉพาะ status_order
            db.session.execute(
                text("UPDATE orderitem SET status_order = :new_status WHERE order_item_id = :order_item_id"),
                {"new_status": new_status, "order_item_id": str(order_item_id)}
            )

        db.session.commit()
        return jsonify({"message": "Status of order updated!", "new_status": new_status}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Function to cancel an order by order and orderitem
def cancel_order():
    try:
        # รับข้อมูลจาก JSON
        data = request.get_json()

        # ตรวจสอบว่ามีข้อมูลที่จำเป็นหรือไม่
        required_keys = ['order', 'orderitem']
        valid, message = validate_input(data, required_keys)
        if not valid:
            return jsonify({"message": message}), 400

        order_id = data['order']
        order_item_id = data['orderitem']

        # ตรวจสอบว่า order_id เป็นตัวเลขที่ถูกต้อง
        if not isinstance(order_id, int) or not isinstance(order_item_id, int):
            return jsonify({"message": "'order' and 'orderitem' must be integers!"}), 400

        # ลบ order item
        order_item = OrderItem.query.get(order_item_id)
        if order_item:
            db.session.delete(order_item)

        # ลบ order ถ้าไม่มี order item อื่นแล้ว
        order = Order.query.get(order_id)
        if order:
            remaining_items = db.session.execute(
                text("SELECT * FROM orderitem WHERE order_id = :order_id"),
                {"order_id": order_id}
            ).fetchall()
            if not remaining_items:
                db.session.delete(order)

        db.session.commit()
        return jsonify({"message": "Order and orderitem cancelled successfully!"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500

# Waste order function
def waste_order():
    try:
        data = request.get_json()

        required_keys = ['order_item_id', 'type', 'quantity', 'reason', 'note']
        valid, message = validate_input(data, required_keys)
        if not valid:
            return jsonify({"message": message}), 400

        # ดึงข้อมูลจาก JSON
        waste_id = data['order_item_id']
        waste_type = data['type']
        quantity = data['quantity']
        reason = data['reason']
        note = data['note']

        # หาก type เป็น ingredients
        if waste_type == "ingredients":
            ingredient = db.session.query(Ingredients).filter_by(id=waste_id).first()

            if not ingredient:
                return jsonify({"message": "Ingredients not found!"}), 404

            # เตรียมข้อมูลเพื่อนำไป insert
            waste_item = Waste(
                item_name=ingredient.ingredients_name,
                quantity=quantity,
                unit=ingredient.unit,
                price=0,
                waste_date=datetime.now(),
                reason=reason,
                note=note
            )
            db.session.add(waste_item)
            db.session.commit()

            # ลบ ingredient ที่ระบุ
            db.session.delete(ingredient)
            db.session.commit()

        # หาก type เป็น order
        elif waste_type == "order":
            order_item = db.session.query(OrderItem).filter_by(order_item_id=waste_id).first()

            if not order_item:
                return jsonify({"message": "Order item not found!"}), 404

            # ดึงข้อมูลจากเมนู
            menu_item = db.session.query(Menu).filter_by(id=order_item.menu_id).first()

            if not menu_item:
                return jsonify({"message": "Menu item not found!"}), 404

            # คำนวณราคา
            price = menu_item.price * quantity

            # เตรียมข้อมูลเพื่อนำไป insert
            waste_item = Waste(
                item_name=menu_item.name,
                quantity=quantity,
                unit="รายการ",
                price=price,
                waste_date=datetime.now(),
                reason=reason,
                note=note
            )
            db.session.add(waste_item)
            db.session.commit()

            # ลบ order item ที่ระบุ
            db.session.delete(order_item)
            db.session.commit()

        else:
            return jsonify({"message": "Invalid type, must be 'order' or 'ingredients'!"}), 400

        return jsonify({"message": "Waste order processed successfully!"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected Error: {str(e)}"}), 500
