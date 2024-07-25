from flask import Flask, request, jsonify
import serial

app = Flask(__name__)

# 아두이노와의 시리얼 통신 설정
SERIAL_PORT = '/dev/ttyUSB0'  # 아두이노가 연결된 포트로 교체 필요
BAUD_RATE = 9600

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)

# 모델 서버 URL
MODEL_SERVER_URL = 'http://model-server-url.com/predict'
# 메인 서버 URL
MAIN_SERVER_URL = 'http://main-server-url.com/sensor-data'

# 사진 캡처 및 모델 서버로 전송
@app.route('/capture', methods=['GET'])
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({'error': 'Cannot open camera'}), 500

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({'error': 'Failed to capture image'}), 500

    image_path = '/tmp/captured_image.jpg'
    cv2.imwrite(image_path, frame)
    
    with open(image_path, 'rb') as img_file:
        response = requests.post(MODEL_SERVER_URL, files={'file': img_file})
    
    os.remove(image_path)
    return jsonify(response.json())

# 센서 데이터 메인 서버로 전송 및 React에 이미지 전송
@app.route('/sensor', methods=['POST'])
def handle_sensor_data_and_capture_image():
    sensor_data = request.json
    if not sensor_data:
        return jsonify({'error': 'No sensor data provided'}), 400

    # 센서 데이터를 메인 서버로 전송하는 함수
    def send_sensor_data_to_main_server(sensor_data):
        response = requests.post(MAIN_SERVER_URL, json=sensor_data)
        return response.json()

    # 이미지를 캡처하고 React로 전송하는 함수
    def capture_image():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {'error': 'Cannot open camera'}

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {'error': 'Failed to capture image'}

        image_path = '/tmp/captured_image.jpg'
        cv2.imwrite(image_path, frame)
        return image_path

    # 센서 데이터를 메인 서버로 전송
    sensor_response = send_sensor_data_to_main_server(sensor_data)

    # 이미지를 캡처하여 파일 경로를 반환
    image_path = capture_image()
    if 'error' in image_path:
        return jsonify(image_path), 500

    # 이미지를 React에 전송
    return send_file(image_path, mimetype='image/jpeg')

# GET 요청으로 PASS 또는 FAIL 값을 받아서 아두이노로 전송
@app.route('/send', methods=['GET'])
def send_to_arduino():
    status = request.args.get('status') #쿼리 문자열에서  status항목값 가져옴
    if status not in ['PASS', 'FAIL']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        arduino.write(status.encode()) #아두이노로 값 전송
        return jsonify({'message': f'Sent {status} to Arduino'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)