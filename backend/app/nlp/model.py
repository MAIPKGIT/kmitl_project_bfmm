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

@cross_origin(supports_credentials=True)
def upload_audio():
    file = request.files["file"]
    
    # Use os.path.expanduser() to properly handle tilde in paths
    base_dir = os.path.expanduser("~/project-deploy-1/backend/app/nlp")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    temp_upload_path = os.path.join(output_dir, file.filename)
    fixed_wav_path = os.path.join(output_dir, "speech.wav")

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
        # temp_upload_path = fixed_wav_path  
        audio_wav = fixed_wav_path
        text = recognize_audio(audio_wav)
        text_new = convert_text(text)
        result = predict_resp(text_new)
    
        return jsonify({"text": text, "result": result}), 200
    else:
        print("✅ File is a real MP3, converting MP3 to WAV...")
        audio = AudioSegment.from_file(temp_upload_path, format="mp3")
        audio.export(fixed_wav_path, format="wav", parameters=["-acodec", "pcm_s16le"])
        print(f"✅ Exported WAV file: {fixed_wav_path}")
        
        # Add speech recognition and processing for MP3 case
        text = recognize_audio(fixed_wav_path)
        text_new = convert_text(text)
        result = predict_resp(text_new)
        
        return jsonify({"text": text, "result": result}), 200

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

model_path = os.path.abspath(os.path.expanduser('~/project-deploy-1/backend/app/nlp/crf_model_ner_v1'))

# Check if the model file actually exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"CRF model file not found at: {model_path}")
    
print(f"Loading CRF model from: {model_path}")

# Create model with the absolute path
crf_model = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=500,
    all_possible_transitions=True,
    model_filename=model_path
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
    # print(word_cut)
    list_word=pos_tag(word_cut,engine='perceptron')
    # print(list_word)
    X_test = extract_features([(data,list_word[i][1]) for i,data in enumerate(word_cut)])
    # print(X_test)
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
                # 🔹 ใช้ fuzzy matching หาชื่อเมนูที่ใกล้เคียงที่สุด
                best_match = process.extractOne(matched_food, menu_list)
                if best_match and best_match[1] > 60:  # เช็ค threshold
                    result["FOOD"].append(best_match[0])  # ใช้ชื่อเมนูที่แมตช์มากที่สุด
                else:
                    result["FOOD"].append(matched_food)  # ถ้าไม่แมตช์เลย ให้ใช้ชื่อเดิม
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

