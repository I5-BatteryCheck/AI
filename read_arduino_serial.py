import serial
import requests
ser=serial.Serial('/dev/ttyACM0',9600,timeout=1)
url -'http://127.0.0.1:8080/capture'

while True:
    if ser.in_waiting >0:
        line=ser.readline().decode('utf-8').strip()
        if line =='CAPTURE':
            response=requests.post(url)
            print(response.status_code)
            print(response.text)