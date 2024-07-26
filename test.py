
import os
import cv2
import requests
from PIL import Image
import numpy as np
from flask import Flask, jsonify,render_template, request
import json


app = Flask(__name__)

# 라즈베리로부터 데이터를 받음 -> 
#                              이미지 모델로 
#                             
@app.route('/test', methods=['POST'])
def read_sensor():
    try:
        print("welcome")
        uploaded_files = request.files
        print(1)
        print(uploaded_files)
        saved_files = []
        for file_key in uploaded_files:
            print(2)
            print(file_key)
            file = uploaded_files[file_key]
            print(3)
            print(file)
            file_path = os.path.join('./', file.filename)
            file.save(file_path)
            saved_files.append(file.filename)

        with open('./data.json', 'r') as file:
            data = json.load(file)

        print(data)
        print(saved_files)

        res = {'status': 'success',
               'files' : saved_files}
        
        return jsonify(res)

    except:
        print('image_error')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)