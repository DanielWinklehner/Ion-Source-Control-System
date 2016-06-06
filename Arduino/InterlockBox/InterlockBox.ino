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

// Flow Sensor Variables:
#define FlowSensor1 2
volatile int flow_sensor1_freq = 0;
int flow_sensor1_freq_write = 0;
unsigned long currentTime;
unsigned long cloopTime;

// Solenoid Valve Variables
const int solenoidValvePins[] = {13, 31}; // Make this 30, 31. 13 is for the in-built LED and so is for testing purpose only.
bool solenoidValveValues[] = {LOW, LOW};

// Micro Switches for interlocks
const int microSwitchPins[] = {28, 29}; 
bool microSwitchValues[] = {LOW, LOW};


// Communication Variables:
char deviceId[37];
bool deviceIdentified = false;
String inputCommand;


void setup()   { 
  // Initialise the Arduino data pins for OUTPUT

  // Microswitches.
  for (unsigned i = 0; i < sizeof(microSwitchPins) / sizeof(int); i++) {
    pinMode(microSwitchPins[i], INPUT);
  }

  // Solenoid Valves.
  for (unsigned i = 0; i < sizeof(solenoidValvePins) / sizeof(int); i++) {
    pinMode(solenoidValvePins[i], OUTPUT);
  }
  
  
  pinMode(FlowSensor1, INPUT);

  pinMode(13, OUTPUT);  // Inbuild LED.
  
  Serial.begin(115200);
//  Serial.begin(128000);

  // Get this Arduino's device ID from memory
  for (int i=0; i < 36; i++) {
    deviceId[i] = EEPROM.read(i);
  }
  attachInterrupt(digitalPinToInterrupt(FlowSensor1), flow_interrupt1, RISING);
}

void flow_interrupt1() {
  flow_sensor1_freq++;
}

String get_serial_data() {
  String content = "";
  char character;

  while(Serial.available()) {
      character = Serial.read();
      content.concat(character);
      delay(2);
  }

  return content;
}

void loop() {


  // For testing purpose only.
  if (solenoidValveValues[0]) {
    digitalWrite(13, HIGH);
  }
  else {
    digitalWrite(13, LOW);
  }
  
  // Flow Meters:
  currentTime = millis();
  // Every second, calculate and print litres/hour
  if(currentTime >= (cloopTime + 1000))
  {
    cloopTime = currentTime; // Updates cloopTime
    flow_sensor1_freq_write = flow_sensor1_freq; //
    flow_sensor1_freq = 0; // Reset Counter    
  }

  // Read microswtiches.
  for (unsigned i = 0; i < sizeof(microSwitchPins) / sizeof(int); i++) {
    microSwitchValues[i] = digitalRead(microSwitchPins[i]);
  }
  

  // GUI Communication.
  
  if (Serial.available()) {
    
    //  inputCommand = Serial.readString();
    inputCommand = get_serial_data();
    
    int first = inputCommand.indexOf(":");
    int second = inputCommand.indexOf("=");
  
    String keyword = inputCommand.substring(0, first);
    String header = inputCommand.substring(first + 1, second);
    String value = inputCommand.substring(second + 1, inputCommand.length());


    int serialNumberCharacterIndex = header.indexOf("#");
    String serialNumber = header.substring(serialNumberCharacterIndex + 1, header.length());

    String filtered_header;
    if (serialNumberCharacterIndex > -1) {
      filtered_header = header.substring(0, serialNumberCharacterIndex);
    }
    else {
      filtered_header = header;
    }

    
    if (keyword == "query") {
      if (filtered_header == "identification") {
        Serial.print("output:device_id=");
        Serial.println(deviceId);
      }
      else if (filtered_header == "micro_switch") {
        if (serialNumber.toInt() < (sizeof(microSwitchPins) / sizeof(int))) {
          Serial.print("output:micro_switch_" + serialNumber + "=");
          Serial.println(microSwitchValues[serialNumber.toInt() - 1]);  // We need to subtract 1 because array counting starts from 0 whereas our label counters (micro_switch#1) start from 1.
        }
      }
      else if (header == "flow_meter_1") {
        Serial.print("output:flow_meter_1=");
        //Serial.println(flow_sensor1_freq_write, DEC);
        Serial.println(random(100) - random(100));
      }
    }
    else if (keyword == "set") {  
      if (filtered_header == "identified") {
        if (value == "1") {
          deviceIdentified = true;
        }
      }
      else if (filtered_header == "solenoid_valve") {
        if (value == "1") {
          if (digitalRead(solenoidValvePins[serialNumber.toInt() - 1]) == LOW) {
            digitalWrite(solenoidValvePins[serialNumber.toInt() - 1], HIGH);   
            solenoidValveValues[serialNumber.toInt() - 1] = HIGH;   
            Serial.println("assigned:solenoid_valve#" + serialNumber + "=HIGH");
          }
        }
        else {
          digitalWrite(solenoidValvePins[serialNumber.toInt() - 1], LOW);        
          solenoidValveValues[serialNumber.toInt() - 1] = LOW;   
          Serial.println("assigned:solenoid_valve#" + serialNumber + "=LOW");
        } 
       }

       }
     //Serial.println("assigned:" + header + "=" + value);
    }
  }



