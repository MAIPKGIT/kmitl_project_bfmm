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
ffmpeg_path = r"D:\ffmpeg\ffmpeg\bin" #เปลี่ยน path ให้ตรงตามเครื่องของตนเอง
os.environ["PATH"] += os.pathsep + ffmpeg_path

AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffmpeg = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")

print(f"Using ffmpeg: {AudioSegment.converter}")  # ตรวจสอบว่า ffmpeg ถูกต้อง

@cross_origin(supports_credentials=True)
def upload_audio():
    file = request.files["file"]
    
    output_dir = r"D:\KMITL\final_project_kmitl\เริ่มใหม่เทอม_2\BFMM\kmitl_project_bfmm\backend\app\nlp\output" #เปลี่ยน path ให้ตรงตามเครื่องของตนเอง
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
            "ffmpeg","-y", "-i", temp_upload_path,
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
        result = predict_resp(text_new)  # การประมวลผลจาก AI

        # ใช้ข้อมูลที่ได้จาก AI ในการเรียกฟังก์ชัน change_status_order
        change_status_order(result)  # ส่งผลลัพธ์จาก predict_resp()

        return jsonify({"text": text, "result": result}), 200
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

menu_list = ["ข้าวกระเพราแซ่บเนื้อไข่ดาว", "กระเพราหมูกรอบ", "กระเพราทะเล", "ข้าวผัดกุ้ง", "ต้มยำกุ้ง"]

print("testtest")

model = r'D:\KMITL\final_project_kmitl\เริ่มใหม่เทอม_2\BFMM\kmitl_project_bfmm\backend\app\nlp\crf_model_ner_v1' #เปลี่ยน path ให้ตรงตามเครื่องของตนเอง แต่เก็บ \crf_model_ner_v1 เอาไว้
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

def change_status_order(ai_data):
    try:
        print("❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤❤")
        print(f"Data received from AI: {ai_data}")

        # ตรวจสอบว่าข้อมูลที่ได้จาก AI ถูกต้องครบถ้วนหรือไม่
        required_keys = ['TABLE', 'COMMAND', 'FOOD']  # แก้ไขให้ตรงกับข้อมูลที่ได้รับ
        valid, message = validate_input(ai_data, required_keys)
        if not valid:
            print("ขั้นตอนที่ 1: ข้อมูลจาก AI ไม่ครบถ้วน:", message)
            return jsonify({"message": message}), 400

        table_id = ai_data['TABLE'][0]  # ใช้ค่า table จาก ai_data
        command_type = ai_data['COMMAND']  # ใช้ค่า command จาก ai_data
        food_name = ai_data['FOOD'][0]  # ใช้ชื่ออาหารจาก ai_data

        # ตรวจสอบว่า command_type เป็นค่า valid หรือไม่
        print(f"ขั้นตอนที่ 2: ตรวจสอบ command_type = {command_type}")
        if command_type not in ['COMMAND_1', 'COMMAND_2']:
            print(f"ข้อผิดพลาด: 'command_type' ต้องเป็น 'COMMAND_1' หรือ 'COMMAND_2', พบ {command_type}")
            return jsonify({"message": "'command_type' must be either 'COMMAND_1' or 'COMMAND_2'!"}), 400

        # ค้นหา ID ของเมนูจากชื่ออาหาร
        print(f"ขั้นตอนที่ 3: ค้นหาข้อมูลเมนูจากชื่ออาหาร {food_name}")
        menu = db.session.execute(
            text("SELECT id FROM menu WHERE name = :food_name"),
            {"food_name": food_name}
        ).mappings().fetchone()

        if not menu:
            print(f"ข้อผิดพลาด: ไม่พบอาหารในเมนูที่ชื่อ '{food_name}'")
            return jsonify({"message": "Food not found in menu!"}), 404

        menu_id = menu['id']
        print(f"ได้ menu_id = {menu_id} จากชื่ออาหาร {food_name}")

        # ขั้นตอนที่ 4: หา order_id จาก table_id ที่ได้รับจาก AI
        print(f"ขั้นตอนที่ 4: หา order_id จาก table_id {table_id} ที่ได้รับจาก AI")
        order_query = db.session.query(Order).filter_by(table_id=table_id).first()
        
        # ตรวจสอบว่า order_query มีข้อมูลหรือไม่
        if not order_query:
            print(f"ข้อผิดพลาด: ไม่พบคำสั่งซื้อที่ active สำหรับ table_id {table_id}")
            return jsonify({"message": f"No active order found for table {table_id}"}), 404

        print(f"order_query: {order_query}")  # ตรวจสอบว่าได้ข้อมูลอะไรจากฐานข้อมูล
        order_id = order_query.order_id
        print(f"ได้ order_id = {order_id} สำหรับ table_id {table_id}")

        # ขั้นตอนที่ 5: เปลี่ยนสถานะ order
        print(f"ขั้นตอนที่ 5: เปลี่ยนสถานะคำสั่งซื้อ: {order_id} สำหรับอาหาร {food_name}")

        # กำหนดค่าของ status ตาม command_type
        status_mapping = {
            'COMMAND_1': 1,
            'COMMAND_2': 2
        }

        # ตรวจสอบว่า command_type อยู่ใน status_mapping หรือไม่
        status = status_mapping.get(command_type)

        if status is None:
            print(f"ข้อผิดพลาด: ไม่พบค่าที่แมตช์สำหรับ command_type: {command_type}")
            return jsonify({"message": f"Invalid command_type: {command_type}"}), 400

        # อัพเดต status_order ในฐานข้อมูล
        db.session.execute(
            text("UPDATE orderitem SET status_order = :status WHERE menu_id = :menu_id AND order_id = :order_id"),
            {"status": status, "menu_id": menu_id, "order_id": order_id}
        )
        db.session.commit()

        return jsonify({"message": "Status updated successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ข้อผิดพลาดใน SQLAlchemyError: {str(e)}")
        return jsonify({"message": str(e)}), 500
    except Exception as e:
        print(f"ข้อผิดพลาดทั่วไป: {str(e)}")
        return jsonify({"message": str(e)}), 500




