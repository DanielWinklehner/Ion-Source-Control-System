/*********************************************************************
This is an example for our Monochrome OLEDs based on SSD1306 drivers

  Pick one up today in the adafruit shop!
  ------> http://www.adafruit.com/category/63_98

This example is for a 128x64 size display using I2C to communicate
3 pins are required to interface (2 I2C and one reset)

Adafruit invests time and resources providing this open source code, 
please support Adafruit and open-source hardware by purchasing 
products from Adafruit!

Written by Limor Fried/Ladyada  for Adafruit Industries.  
BSD license, check license.txt for more information
All text above, and the splash screen must be included in any redistribution
*********************************************************************/

#include <SPI.h>
#include <Wire.h>
#include <EEPROM.h>




char deviceId[37];
bool deviceIdentified = false;
String inputCommand;
/* 
 *  States: What state the device is on; because you can't really do multi-threadding with Arduinos, we need to keep track of what "state" the device is on to decide what we want the Arduino to do.
 *  
 *  
 */
enum DeviceState {
  identification,
  sending_output,
  receiving_input,
  resting
};



DeviceState currentDeviceState = resting;



bool microSwitch = LOW;
bool solenoidValve = LOW;

void setup()   { 
  // Initialise the Arduino data pins for OUTPUT

  pinMode(50, OUTPUT);  // Solenoid Valve.
  pinMode(51, INPUT);   // Microswitch.

  // Get the device ID.
  Serial.begin(9600);

  for (int i=0; i < 36; i++) {
    deviceId[i] = EEPROM.read(i);
  }
  
}

void loop() {
  delay(50);

  microSwitch = digitalRead(51);

  // GUI Communication.
  
  inputCommand = Serial.readString();
  
  int first = inputCommand.indexOf(":");
  int second = inputCommand.indexOf("=");

  String keyword = inputCommand.substring(0, first);
  String header = inputCommand.substring(first + 1, second);
  String value = inputCommand.substring(second + 1, inputCommand.length());

  if (keyword == "query") {

    if (header == "identification") {
      Serial.print("output:device_id=");
      Serial.println(deviceId);
    }
    else if (header == "reed_switch_1") {
      Serial.println("output:reed_switch_1=" + microSwitch);
    }
    
    
  }
  else if (keyword == "set") {
    
    if (header == "identified") {
      if (value == "1") {
        currentDeviceState = resting;
      }
    }
    else if (header == "solenoid_valve_1") {
      if (value == "1") {
        if ( solenoidValve == LOW) {
          digitalWrite(50, HIGH);
          solenoidValve = HIGH;
        }
        else {
          digitalWrite(50, LOW);
          solenoidValve = LOW;
        }
      }
      else {
       // Code to stop the gauge? 
      }
    }
    

    Serial.println("assigned:" + header + "=" + value);
    
  }
  
}



