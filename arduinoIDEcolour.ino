// Arduino Code

#include <Wire.h>
#include <Adafruit_TCS34725.h>


const int DMD_OUT = 3;
String x;
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_2_4MS, TCS34725_GAIN_16X);


void setup() {
  Serial.begin(9600);
  if (!tcs.begin()) {
    Serial.println("Error initializing TCS34725 sensor!");
    while (1);
  }
  //pinMode(DMD_OUT, INPUT);
  //attachInterrupt(digitalPinToInterrupt(DMD_OUT), handleInterrupt, FALLING);
}

void loop() {
  while (!Serial.available());
  x = Serial.readStringUntil('\n');
  x.trim(); // Remove any whitespace
  Serial.print("Received command: ");
  Serial.println(x);
  if (x=="START"){
    attachInterrupt(digitalPinToInterrupt(DMD_OUT), handleInterrupt, FALLING);
  }
  else if (x == "STOP") {
    detachInterrupt(digitalPinToInterrupt(DMD_OUT));
  }
  else if (x == "TEST") {
    Serial.println("1");
  }
}


void handleInterrupt() {
  // Trigger sensor reading
  uint16_t red, green, blue, clear;
  tcs.getRawData(&red, &green, &blue, &clear);
  // Send sensor data over serial
  Serial.print(red);

}



