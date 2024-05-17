/*
 		Board pin | NodeMCU GPIO | 	Arduino IDE
 					A- 										1 												5 or D1
 					A+ 										3 												0 or D3
 					B- 										2 												4 or D2
 					B+ 										4 												2 or D4
*/

#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>


#ifndef STASSID
#define STASSID "Studiogo-2.4G"
#define STAPSK "luckyhousepro"
#endif


// Replace with your network credentials
const char* ssid = "Studiogo-2.4G";
const char* password = "luckyhousepro";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);


bool state = 0;

const int PWMA=D1;//Right side 
const int PWMB=D2;//Left side 
const int DA=D3;//Right reverse 
const int DB=D4;//Left reverse 

unsigned long previousMillis = 0;
unsigned long interval = 0; // Interval for each step (in milliseconds)
int step = 0; // Track the current step


void go() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // Update previousMillis for the next step
    previousMillis = currentMillis;

    // Set random interval
    interval = random(1000, 5000); // Random delay between 1 to 5 seconds

    // Set random movement
    int randomMovement = random(6); // Generate a random number between 0 to 5

    // Set random speed
    // int randomSpeed = random(250, 250); // Random speed between 50% to 100%
    int randomSpeed = 500;

    // Apply PWM by Software for speed control
    analogWrite(PWMA, randomSpeed); // Apply PWM to simulate speed control
    analogWrite(PWMB, randomSpeed); // Apply PWM to simulate speed control

    // Execute the random movement
    switch (randomMovement) {
      case 0:
        digitalWrite(DA, LOW);
        digitalWrite(DB, LOW);
        break;
      case 1:
        digitalWrite(DA, HIGH);
        digitalWrite(DB, LOW);
        break;
      case 2:
        digitalWrite(DA, HIGH);
        digitalWrite(DB, HIGH);
        break;
      case 3:
        digitalWrite(DA, LOW);
        digitalWrite(DB, HIGH);
        break;
      case 4:
        digitalWrite(DA, HIGH);
        digitalWrite(DB, HIGH);
        break;
      case 5:
        digitalWrite(DA, LOW);
        digitalWrite(DB, LOW);
        break;
    }
  }
}


void stop(){
  digitalWrite(PWMA, 0); 
  digitalWrite(DA, LOW); 
     
  digitalWrite(PWMB, 0); 
  digitalWrite(DB, LOW);
}


void setup(void) {
  Serial.begin(115200);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  // Print ESP Local IP Address
  Serial.println(WiFi.localIP());

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/plain", "hello from esp8266!\r\n");
  });

  server.on("/on", HTTP_GET, [](AsyncWebServerRequest *request){
    state = 1;
    request->send_P(200, "text/plain", "on");
  });

  server.on("/off", HTTP_GET, [](AsyncWebServerRequest *request){
    state = 0;
    request->send_P(200, "text/plain", "off");
  });

  // Start server
  server.begin();

  pinMode(PWMA, OUTPUT); 
  pinMode(PWMB, OUTPUT); 
  pinMode(DA, OUTPUT); 
  pinMode(DB, OUTPUT); 
 	Serial.println("Motor SHield 12E Initialized");
}

void loop() {
  switch(state){
    case 0:
    stop();
    break;
    case 1:
    go();
    break;
    }
}

