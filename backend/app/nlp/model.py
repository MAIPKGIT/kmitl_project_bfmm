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

import re
from flask import Flask, request, jsonify
import speech_recognition as sr
import io
import os
import subprocess
from pydub import AudioSegment
import speech_recognition as sr
from flask_cors import cross_origin
from pydub.utils import which

# ตั้งค่า ffmpeg path
ffmpeg_path = r"C:\F_Utility\ffmpeg-master-latest-win64-gpl-shared\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffmpeg = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")

print(f"Using ffmpeg: {AudioSegment.converter}")  # ตรวจสอบว่า ffmpeg ถูกต้อง

@cross_origin(supports_credentials=True)
def upload_audio():
    file = request.files["file"]
    
    output_dir = r"C:\F_University\Mile_24-2-68\Project\Backend\app\nlp\output"
    os.makedirs(output_dir, exist_ok=True)

    temp_upload_path = os.path.join(output_dir, file.filename)
    fixed_wav_path = "speech.wav"

    with open(temp_upload_path, "wb") as f:
        f.write(file.read())

    print(f"File uploaded to: {temp_upload_path}")

    ffmpeg_check_cmd = ["ffmpeg", "-i", temp_upload_path]
    result = subprocess.run(ffmpeg_check_cmd, stderr=subprocess.PIPE, text=True)

    if "matroska,webm" in result.stderr or "opus" in result.stderr:
        print("⚠️ Detected WebM/Opus file, converting to WAV...")

        convert_cmd = [
            "ffmpeg", "-y", "-i", temp_upload_path,
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            fixed_wav_path
        ]
        subprocess.run(convert_cmd, check=True)

        print(f"✅ Converted to WAV: {fixed_wav_path}")
        audio_wav = "speech.wav"
        text = recognize_audio(audio_wav)
        text_new = convert_text(text)
        result_data = predict_resp(text_new)

        # เรียกใช้ change_status_order
        return change_status_order(result_data)
    else:
        print("✅ File is a real MP3, converting MP3 to WAV...")
        audio = AudioSegment.from_file(temp_upload_path, format="mp3")
        audio.export(fixed_wav_path, format="wav", parameters=["-acodec", "pcm_s16le"])
        print(f"✅ Exported WAV file: {fixed_wav_path}")

    if not os.path.exists(fixed_wav_path) or os.path.getsize(fixed_wav_path) == 0:
        return jsonify({"error": "WAV file is empty or conversion failed"}), 500

    return jsonify({"text": "Conversion successful", "wav_file": fixed_wav_path}), 200


def recognize_audio(audio_stream):
    recog = sr.Recognizer()
    with sr.AudioFile(audio_stream) as source:
        audio = recog.record(source)

    try:
        text = recog.recognize_google(audio, language="th-TH")
        return text
    except sr.UnknownValueError:
        return "ไม่สามารถแปลงเสียงได้"
    except sr.RequestError:
        return "เกิดข้อผิดพลาดในการเชื่อมต่อกับ API"
    
def convert_text(text):
    number_map = {
        "ศูนย์": "0", "หนึ่ง": "1", "สอง": "2", "สาม": "3", "สี่": "4",
        "ห้า": "5", "หก": "6", "เจ็ด": "7", "แปด": "8", "เก้า": "9", "สิบ": "10", 
        "pizza": "พิซซ่า"
    }
    
    for thai_num, arabic_num in number_map.items():
        text = text.replace(thai_num, arabic_num)
    text = re.sub(r"\s+", "", text)
    
    return text 

import sklearn_crfsuite
from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from rapidfuzz import process
from app.models.menu import Menu

# menu_list = ["ข้าวกระเพราแซ่บเนื้อไข่ดาว", "กระเพราหมูกรอบ", "กระเพราทะเล", "ข้าวผัดกุ้ง", "ต้มยำกุ้ง"]

model = r'C:\F_University\Mile_24-2-68\Project\Backend\app\nlp\crf_model_ner_v1'
crf_model = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=500,
    all_possible_transitions=True,
    model_filename=model
)

def doc2features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]
    features = {
        'word.word': word,
        'word.isspace':word.isspace(),
        'postag':postag,
        'word.isdigit()': word.isdigit()
    }
    if i > 0:
        prevword = doc[i-1][0]
        postag1 = doc[i-1][1]
        features['word.prevword'] = prevword
        features['word.previsspace'] = prevword.isspace()
        features['word.prepostag'] = postag1
        features['word.prevwordisdigit'] = prevword.isdigit()
    else:
        features['BOS'] = True
    if i < len(doc)-1:
        nextword = doc[i+1][0]
        postag1 = doc[i+1][1]
        features['word.nextword'] = nextword
        features['word.nextisspace'] = nextword.isspace()
        features['word.nextpostag'] = postag1
        features['word.nextwordisdigit'] = nextword.isdigit()
    else:
        features['EOS'] = True
    return features

def extract_features(doc):
    return [doc2features(doc, i) for i in range(len(doc))]

def postag(text):
    listtxt = [i for i in text.split('\n') if i!='']
    list_word = []
    for data in listtxt:
        list_word.append(data.split('\t')[0])
    list_word=pos_tag(list_word,engine="perceptron")
    text=""
    i=0
    for data in listtxt:
        text+=data.split('\t')[0]+'\t'+list_word[i][1]+'\t'+data.split('\t')[1]+'\n'
        i+=1
    return text

def get_ner(text):
    word_cut=word_tokenize(text,keep_whitespace=False)
    list_word=pos_tag(word_cut,engine='perceptron')
    X_test = extract_features([(data,list_word[i][1]) for i,data in enumerate(word_cut)])
    y_=crf_model.predict_single(X_test)
    return [(word_cut[i],list_word[i][1],data) for i,data in enumerate(y_)]


def process_data(data):
    
    result = {"TABLE": [], "COMMAND": "", "FOOD": [], "QUESTION": False}
    current_table = None
    current_food = []

    menu_list = Menu.query.all()
    menu_list = [menu.name for menu in menu_list]
    
    for word, tag, label in data:
        if label.startswith("B-TABLE"):
            if word.isdigit():
                current_table = word
            else:
                current_table = None
        elif label.startswith("I-TABLE") and current_table is None:
            if word.isdigit():
                current_table = word
        elif label.startswith("I-TABLE") and current_table is not None:
            if word.isdigit():
                current_table += word
        elif label.startswith("B-FOOD"):
            current_food = [word]
        elif label.startswith("I-FOOD"):
            current_food.append(word)
        elif label.startswith("B-COMMAND_"):
            result["COMMAND"] = "COMMAND_" + label.split("_")[1]
        elif label.startswith("B-QUESTION"):
            result["QUESTION"] = True
        elif label == "O":
            if current_table is not None and current_table.isdigit():
                result["TABLE"].append(int(current_table))
                current_table = None
            if current_food:
                matched_food = "".join(current_food)
                best_match = process.extractOne(matched_food, menu_list)
                if best_match and best_match[1] > 60:
                    result["FOOD"].append(best_match[0])
                else:
                    result["FOOD"].append(matched_food)
                current_food = []
    
    if current_table is not None and current_table.isdigit():
        result["TABLE"].append(int(current_table))
    if current_food:
        matched_food = "".join(current_food)
        best_match = process.extractOne(matched_food, menu_list)
        if best_match and best_match[1] > 60:
            result["FOOD"].append(best_match[0])
        else:
            result["FOOD"].append(matched_food)
    
    return result

def predict_resp(txt):
    p_data = get_ner(txt)
    return process_data(p_data)

# Utility function for input validation
def validate_input(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False, f"{key} is required!"
    return True, ""

def stock_manager(menu_id, qty):
    try:
        print("📦 เริ่มระบบ stock_manager...")

        # --- 1. จัดการ stock วัตถุดิบจาก table 'menuingredients' ---
        print(f"🔍 ดึงวัตถุดิบเดี่ยวของ menu_id: {menu_id}")
        menu_ingredients = db.session.execute(
            text("SELECT ingredient_id, volume FROM menuingredients WHERE menu_id = :menu_id"),
            {"menu_id": menu_id}
        ).mappings().fetchall()

        if not menu_ingredients:
            print("⚠️ ไม่พบข้อมูลใน menuingredients")

        ingredient_ids = [ingredient["ingredient_id"] for ingredient in menu_ingredients]

        ingredient_stocks = []
        if ingredient_ids:
            ingredient_stocks = db.session.execute(
                text(f"SELECT Ingredients_id, main_stock FROM ingredients WHERE Ingredients_id IN ({', '.join(map(str, ingredient_ids))})")
            ).mappings().fetchall()

        stock_dict = {item["Ingredients_id"]: item["main_stock"] for item in ingredient_stocks}

        for ingredient in menu_ingredients:
            ingredient_id = ingredient["ingredient_id"]
            volume = ingredient["volume"]
            if ingredient_id in stock_dict:
                used_amount = volume * qty
                new_stock = stock_dict[ingredient_id] - used_amount
                print(f"→ ลด stock วัตถุดิบ id {ingredient_id}: -{used_amount}, คงเหลือใหม่: {new_stock}")

                db.session.execute(
                    text("UPDATE ingredients SET main_stock = :new_stock WHERE Ingredients_id = :ingredient_id"),
                    {"new_stock": new_stock, "ingredient_id": ingredient_id}
                )
            else:
                print(f"❗ ไม่พบ ingredient_id {ingredient_id} ใน stock")
                return jsonify({"message": f"Ingredient with id {ingredient_id} not found!"}), 404

        # --- 2. จัดการ stock จากระบบ Pack (menuingredientpack) ---
        print(f"🔍 ดึงวัตถุดิบแบบ Pack ของ menu_id: {menu_id}")
        menu_ingredient_packs = db.session.execute(
            text("SELECT ingredient_pack_id, qty FROM menuingredientpack WHERE menu_id = :menu_id"),
            {"menu_id": menu_id}
        ).mappings().fetchall()

        if not menu_ingredient_packs:
            print("⚠️ ไม่พบข้อมูลใน menuingredientpack")

        pack_ids = [pack["ingredient_pack_id"] for pack in menu_ingredient_packs]

        ingredient_pack_stocks = []
        if pack_ids:
            ingredient_pack_stocks = db.session.execute(
                text(f"SELECT id, stock FROM ingredientpack WHERE id IN ({', '.join(map(str, pack_ids))})")
            ).mappings().fetchall()

        pack_stock_dict = {item["id"]: item["stock"] for item in ingredient_pack_stocks}

        for pack in menu_ingredient_packs:
            pack_id = pack["ingredient_pack_id"]
            pack_qty = pack["qty"]
            if pack_id in pack_stock_dict:
                used_amount = pack_qty * qty
                new_stock = pack_stock_dict[pack_id] - used_amount
                print(f"→ ลด stock Pack id {pack_id}: -{used_amount}, คงเหลือใหม่: {new_stock}")

                db.session.execute(
                    text("UPDATE ingredientpack SET stock = :new_stock WHERE id = :pack_id"),
                    {"new_stock": new_stock, "pack_id": pack_id}
                )
            else:
                print(f"❗ ไม่พบ ingredient_pack_id {pack_id} ใน stock")
                return jsonify({"message": f"Ingredient Pack with id {pack_id} not found!"}), 404

        db.session.commit()
        print("✅ stock_manager ทำงานสำเร็จทั้งหมด")
        return {"status": 200, "message": "Stock has been successfully updated!"}

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Database Error: {str(e)}")
        return {"status": 500, "message": f"Database Error: {str(e)}"}
    except Exception as e:
        db.session.rollback()
        print(f"❌ Unexpected Error: {str(e)}")
        return {"status": 500, "message": f"Unexpected Error: {str(e)}"}

def change_status_order(ai_data):
    try:
        print("❤❤❤ เริ่มต้นเปลี่ยนสถานะคำสั่งซื้อ ❤❤❤")
        print(f"Data received from AI: {ai_data}")

        required_keys = ['TABLE', 'COMMAND', 'FOOD']
        valid, message = validate_input(ai_data, required_keys)
        if not valid:
            return jsonify({"message": message}), 400

        table_id = ai_data['TABLE'][0]
        command_type = ai_data['COMMAND']
        food_name = ai_data['FOOD'][0]

        if command_type not in ['COMMAND_1', 'COMMAND_2']:
            return jsonify({"message": "'command_type' must be either 'COMMAND_1' or 'COMMAND_2'!"}), 400

        # หา menu_id จาก food_name
        menu = db.session.execute(
            text("SELECT id FROM menu WHERE name = :food_name"),
            {"food_name": food_name}
        ).mappings().fetchone()

        if not menu:
            return jsonify({"message": "Food not found in menu!"}), 404

        menu_id = menu['id']

        # หา order_id จาก table_id
        order_query = db.session.query(Order).filter_by(table_id=table_id).first()
        if not order_query:
            return jsonify({"message": f"No active order found for table {table_id}"}), 404

        order_id = order_query.order_id

        # หา status_order เดิม
        existing_status = db.session.execute(
            text("SELECT status_order FROM orderitem WHERE menu_id = :menu_id AND order_id = :order_id"),
            {"menu_id": menu_id, "order_id": order_id}
        ).mappings().fetchone()

        if not existing_status:
            return jsonify({"message": "Order item not found!"}), 404

        current_status = existing_status["status_order"]
        print(f"สถานะเดิมของ orderitem: {current_status}")

        # Mapping command เป็นสถานะใหม่
        status_mapping = {'COMMAND_1': 1, 'COMMAND_2': 2}
        new_status = status_mapping.get(command_type)

        # เช็กว่ามีการลดสถานะไหม (ไม่อนุญาต)
        if new_status <= current_status:
            return jsonify({"message": "ไม่อนุญาตให้ลดสถานะของคำสั่งซื้อ!"}), 400

        # อัปเดตสถานะ
        db.session.execute(
            text("UPDATE orderitem SET status_order = :status WHERE menu_id = :menu_id AND order_id = :order_id"),
            {"status": new_status, "menu_id": menu_id, "order_id": order_id}
        )
        db.session.commit()

        print("✅ อัปเดตสถานะสำเร็จ!")

        # ดึง qty เพื่อส่งไป stock_manager
        qty_result = db.session.execute(
            text("SELECT menu_qty FROM orderitem WHERE menu_id = :menu_id AND order_id = :order_id"),
            {"menu_id": menu_id, "order_id": order_id}
        ).mappings().fetchone()

        # ตรวจสอบผลลัพธ์จากการ query
        if qty_result:
            print(f"Result of qty query: {qty_result}")
            qty = qty_result['menu_qty']  # ดึง menu_qty ที่ได้
        else:
            print(f"No qty found for menu_id: {menu_id} and order_id: {order_id}")
            qty = 0  # หรือกำหนดค่า default หากไม่พบข้อมูล

        if not qty_result:
            print("ไม่พบจำนวน qty ของ orderitem")
            return jsonify({"message": "ไม่พบจำนวน qty ของ orderitem"}), 404

        qty = qty_result["menu_qty"]

        # เรียกใช้งาน stock_manager
        stock_result = stock_manager(menu_id, qty)

        if stock_result["status"] != 200:
            print("Status updated, but stock error occurred!")
            return jsonify({"message": "Status updated, but stock error occurred!", "stock_result": stock_result}), 500

        print("Status updated successfully")
        return jsonify({"message": "Status updated successfully", "stock_result": stock_result}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"SQLAlchemyError : {e}")
        return jsonify({"message": str(e)}), 500
    except Exception as e:
        print(f"Exception : {e}")
        return jsonify({"message": str(e)}), 500
