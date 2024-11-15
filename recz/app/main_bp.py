from flask import Flask, jsonify, request, Blueprint, current_app
import sys
import json
from dataclasses import asdict
from PIL import Image
import base64
import io
import os
import random
from .class_all import ImageResult, IdentifyRes
from .classification import classify

main_bp = Blueprint('main', __name__)

def convert_image(image):
    byte_stream = io.BytesIO(base64.b64decode(image))

    image = Image.open(byte_stream).convert('RGB')

    return image

def save_image(image, save_path):
    byte_stream = io.BytesIO(base64.b64decode(image))
    with open(save_path, "wb") as output_file:
        output_file.write(byte_stream.getvalue())

def generate_two_letters():
    # 生成两个随机字母，可以是大写或小写英文字母
    letter1 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    letter2 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return letter1+letter2

@main_bp.route('/')
def home():
    welcome = current_app.config['WELCOME']
    return welcome

# 定义一个返回JSON数据的路由
@main_bp.route('/data', methods=['POST'])
def data():
    data = request.get_json()

    # 如果 JSON 数据为空，返回错误信息
    if data is None:
        return jsonify({'error': 'Request body is empty or not JSON format'}), 400

    res = IdentifyRes()
    # with open(r"D:\jinhe\0611_addressing 异常.png", "rb") as image_file:
    #     byte_stream = io.BytesIO(image_file.read())

    # base64_string = base64.b64encode(byte_stream.getvalue()).decode("utf-8")
    # print(base64_string)
    
    for item in data["imgs"]:
        img64 = item["iovalue"]
        clsres = classify(convert_image(img64), "resnet50", current_app.config['CKPT_PATH'])
        if clsres == "normal":
            yesorno = "yes"
        else:
            yesorno = "no"
        image_res = ImageResult(name=item["name"], prevalue=yesorno)
        res.imgs.append(image_res)

    json_data = json.dumps(asdict(res), indent=4)
    return json_data

@main_bp.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Request body is empty or not JSON format'}), 400
    
    train_path = current_app.config['TRAINING_PATH']
    image = data["iovalue"]
    prevalue = data["prevalue"]
    filename = data["name"]
    full_path = os.path.join(train_path, prevalue, filename)
    if os.path.exists(full_path):
        base_name, ext = os.path.splitext(filename)
        random_str = generate_two_letters()
        new_filename = f"{base_name}_{random_str}{ext}"
        full_path = os.path.join(train_path, prevalue, new_filename)
    
    save_image(image, full_path)

    return jsonify({'ok': '保存成功'}), 200
    