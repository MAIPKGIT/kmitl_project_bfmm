from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS

# สร้าง instance ของ db และ JWTManager
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # คอนฟิกต่างๆ
    app.config.from_object(Config)
    
    # การตั้งค่า db และ JWTManager
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {
        "origins": "*",             # ✅ อนุญาตทุก Origin
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ อนุญาตทุก Method
        "allow_headers": ["*"],     # ✅ อนุญาตทุก Header
        "supports_credentials": True
    }})

    # import ไฟล์อื่นๆ ภายหลังจากการสร้างแอป
    from app.routes.account_routes import account_bp
    app.register_blueprint(account_bp, url_prefix='/api/account')
    from app.routes.menu_routes import menu_bp
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    from app.routes.menutype_routes import menutype_bp
    app.register_blueprint(menutype_bp, url_prefix='/api/menutype')
    from app.routes.step_routes import step_bp
    app.register_blueprint(step_bp, url_prefix='/api/step')
    from app.routes.history_routes import history_bp
    app.register_blueprint(history_bp, url_prefix='/api/history')
    from app.routes.waste_routes import waste_bp
    app.register_blueprint(waste_bp, url_prefix='/api/waste')
    from app.routes.ingredients_routes import ingredients_bp
    app.register_blueprint(ingredients_bp, url_prefix='/api/ingredients')
    from app.routes.menuingredients_routes import menuingredients_bp
    app.register_blueprint(menuingredients_bp, url_prefix='/api/menuingredients')
    from app.routes.payment_routes import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    from app.routes.order_routes import order_bp
    app.register_blueprint(order_bp, url_prefix='/api/order')
    from app.routes.orderitem_routes import orderitem_bp
    app.register_blueprint(orderitem_bp, url_prefix='/api/orderitem')
    from app.routes.table_routes import table_bp
    app.register_blueprint(table_bp, url_prefix='/api/table')
    from app.routes.ingredientpack_route import ingredientpack_bp
    app.register_blueprint(ingredientpack_bp, url_prefix='/api/ingredientpacks')
    from app.routes.ingredientpackitems_route import ingredientpackitems_bp
    app.register_blueprint(ingredientpackitems_bp, url_prefix='/api/ingredientpackitems')
    from app.routes.menuingredientpack_route import menuingredientpack_bp
    app.register_blueprint(menuingredientpack_bp, url_prefix='/api/menuingredientpack')

    from app.routes.nlp_route import nlp_db
    app.register_blueprint(nlp_db, url_prefix='/api/nlp')

    from app.tests.account_apitest_routes import account_apitest_bp
    app.register_blueprint(account_apitest_bp, url_prefix='/api/test/account')

    return app
