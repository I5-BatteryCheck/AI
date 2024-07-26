import cv2
import requests
#import serial
from flask import Flask, jsonify,render_template, request
from datetime import datetime
from PIL import Image
import json
import numpy as np


app = Flask(__name__)

front_server_url = ['http://192.168.253.253:5005/test']
model_server_url = ['http://192.168.253.253:5005/test']
#arduino = serial.Serial('COM3', 9600)


#사진 촬영 함수
def capture(n, width=0, height=0):
    # 웹캠 열기
    cap = cv2.VideoCapture(n)  # 0은 기본 웹캠을 의미합니다. 다른 웹캠을 사용하려면 인덱스를 조정하세요.

    if width*height !=0:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    # 프레임 읽기
    ret, frame = cap.read()

    if not ret:
        print("프레임을 읽을 수 없습니다.")
        return

    # 리소스 해제
    cap.release()

    return frame

# 현재 시간 구하는 함수
def get_time():
    now = datetime.now()
    now = str(now)
    now = now.split('.')[0]
    now = now.replace('-','').replace(' ','').replace(':','')
    return now



# 0.5초마다 센서값 http 신호 -> 
#                             센서 값 저장
#                             사진 촬영, 센서 값>리액트
sensors_value = {}
@app.route('/sensor', methods=['POST'])
def read_sensor():
    try:
        data = request.get_json()
        data2react = {}
        for key in data.keys():
            sensors_value[key] = data[key]
            data2react[key] = data[key]
        
        for n in range(1):
            data2react[f'image_{n}'] = capture(n, 160, 140)
            
        response = requests.post(front_server_url[0], json = data2react)
        response_data = response.json()
        
    except:
        print('sensor')

    
# capture http신호 ->
#                    최근 센서 값과 사진을 촬영해서 > model
@app.route('/chapture', methods=['POST'])
def read_chapture():
    try:
        print(1)
        data = request.get_json()
        print(2)
        if 1:
            data2model = {}
            #data2model['time'] = get_time()
            print(3)
            for key in sensors_value.keys():
                data2model[key] = sensors_value[key]

            with open('./data.json', 'w') as json_file:
                json.dump(data2model, json_file, indent=4) 
            
            print(4)
            for n in range(1):
                ct = capture(n, 640,480)
                array = ct.astype(np.uint8)
                image = Image.fromarray(array)
                image.save(f'image_{n}.jpg')

            print(5)
            files = {}
            files['data_json'] = ('data.json', open('data.json', 'rb'))
            for n in range(1):
                files[f'image_{n}'] = (f'image_{n}.jpg', open(f'image_{n}.jpg', 'rb'))

            print(6)
            # POST 요청 보내기
            response = requests.post(model_server_url[0], files = files)
            print(7)
            response_data = response.json()
            print(8)
            
    except:
        print('chapture')
 
 
    
# 후처리 결과 http ->
#                   아두이노로 시리얼로 송신 
@app.route('/post_processing', methods=['POST'])
def read_post_processing():
    try:
        data = request.get_json()

        if data:
            data2arduino=data
            data2arduino=data2arduino.encode('utf-8')
            #arduino.write(data2arduino)
        
    except:
        print('post_processing error')
    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)