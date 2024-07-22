/******************************************************************************************
 * FileName     : 02._dht11_oled
 * Description  : 온습도 센서의 값을 시리얼 모니터에 출력해 보기
 * Author       : 박은정
 * Created Date : 2023.08.17
 * Reference    : 
 * Modified     : 
 ******************************************************************************************/
#include "dht11.h"
#include "oled_u8g2.h"
#define DHT11PIN D2 // D2 포트에 DHT11 센서를 연결해야 함

dht11 DHT11; // 온습도 센서
OLED_U8G2 oled;
int light_sensor = A1; // 조도센서

struct SensorData {
  int temperature;
  int humidity;
  int lightLevel;
};

void setup() {
  oled.setup();
  Serial.begin(115200);
}

void loop() {  
 SensorData data = readSensors(); // 센서 값을 읽고 반환받음
  
  // 시리얼 모니터에 출력
  Serial.print("Temperature: ");
  Serial.print(data.temperature); // 온도 값 출력
  Serial.print("℃, Humidity: ");
  Serial.print(data.humidity); // 습도 값 출력
  Serial.print("%, Light Level: ");
  Serial.print(data.lightLevel); // 조도 값 출력
  Serial.println(" lux");

  // OLED 디스플레이에 출력
  //oled.setLine(1, "Sensor Data"); // OLED 모듈 1번째 줄에 저장
  oled.setLine(1, "Temp: " + String(data.temperature) + "C"); // OLED 모듈 2번째 줄에 온도 값 저장
  oled.setLine(2, "Humi: " + String(data.humidity) + "%"); // OLED 모듈 3번째 줄에 습도 값 저장
  oled.setLine(3, "Light: " + String(data.lightLevel) + " lux"); // OLED 모듈 4번째 줄에 조도 값 저장
  oled.display(); // OLED 모듈 출력

  delay(1000); // 1초 대기
}

// DHT11 및 조도센서 값을 읽고 SensorData 구조체로 반환하는 함수
SensorData readSensors() {
  DHT11.read(DHT11PIN); // 온습도 센서(DTH11) 값 측정
  
  SensorData data;
  data.temperature = DHT11.temperature;
  data.humidity = DHT11.humidity;
  data.lightLevel = analogRead(light_sensor); // 조 값 측정

  return data;
}

//=========================================================================================
//
// (주)한국공학기술연구원 http://et.ketri.re.kr
//
//=========================================================================================