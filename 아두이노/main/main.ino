/******************************************************************************************
 * FileName     : main.ino
 * Description  : 온습도 센서, 조도 센서의 값을 HTTP를 통해 0.5초마다 전송
 * Author       : 박기범
 * Created Date : 2024.07.24
 ******************************************************************************************/
#include <WiFi.h>
#include <HTTPClient.h>
#include "dht11.h"
#include "oled_u8g2.h"
#define DHT11PIN D2 // D2 포트에 DHT11 센서를 연결해야 함

const char* ssid = "Ccom";      // WiFi SSID
const char* password = "ccom0414";  // WiFi 비밀번호
dht11 DHT11; // 온습도 센서
OLED_U8G2 oled;
int light_sensor = A1; // 조도센서

struct SensorData {
  int temperature;
  int humidity;
  int lightLevel;
};

void setup() {
  Serial.begin(115200);
  oled.setup();
  setupWiFi();

}

void loop() {  
  SensorData data = readSensors(); // 센서 값을 읽고 반환받음


  serialPrint(data); //시리얼 모니터에 출력 표시
  oledPrint(data); //oled 모듈에 출력 표시

  const char* postServerName = "http://192.168.81.192:8080/"; //URL 수정
  String jsonPayload = createJsonPayload(data);
  httpPostRequest(postServerName, jsonPayload);
  
  delay(500);  // 0.5초 지연
}

void serialPrint(SensorData data){
  // 시리얼 모니터에 출력
  Serial.print("Temperature: ");
  Serial.print(data.temperature); // 온도 값 출력
  Serial.print("℃, Humidity: ");
  Serial.print(data.humidity); // 습도 값 출력
  Serial.print("%, Light Level: ");
  Serial.print(data.lightLevel); // 조도 값 출력
  Serial.println("lux");
}

void oledPrint(SensorData data){
  // OLED 디스플레이에 출력
  //oled.setLine(1, "Sensor Data"); // OLED 모듈 1번째 줄에 저장
  oled.setLine(1, "Temp: " + String(data.temperature) + "C"); // OLED 모듈 1번째 줄에 온도 값 저장
  oled.setLine(2, "Humi: " + String(data.humidity) + "%"); // OLED 모듈 2번째 줄에 습도 값 저장
  oled.setLine(3, "Light: " + String(data.lightLevel) + "lux"); // OLED 모듈 3번째 줄에 조도 값 저장
  oled.display(); // OLED 모듈 출력

}
// DHT11 및 조도센서 값을 읽고 SensorData 구조체로 반환하는 함수
SensorData readSensors() {
  DHT11.read(DHT11PIN); // 온습도 센서(DTH11) 값 측정
  
  SensorData data;
  data.temperature = DHT11.temperature;
  data.humidity = DHT11.humidity;
  data.lightLevel = analogRead(light_sensor); // 조도 값 측정

  return data;
}

void setupWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void httpPostRequest(const char* serverName, String jsonPayload) {
  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println(httpResponseCode);
    Serial.println(response);
  } else {
    Serial.print("Error on HTTP request: ");
    Serial.println(httpResponseCode);
  }
  http.end();
}

String createJsonPayload(SensorData data) {

  String jsonPayload = "{";
  jsonPayload += "\"Temperature\":\"" + String(data.temperature) + "\",";
  jsonPayload += "\"humidity\":\"" + String(data.humidity) + "\",";
  jsonPayload += "\"lightLevel\":\"" + String(data.lightLevel) + "\"";
  jsonPayload += "}";

  Serial.println("JSON Payload: " + jsonPayload); // 디버그를 위해 JSON 출력
  return jsonPayload;
}

//=========================================================================================
//
// SW_Bootcamp I5
//
//=========================================================================================