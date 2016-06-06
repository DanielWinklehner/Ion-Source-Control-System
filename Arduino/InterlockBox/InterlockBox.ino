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
#define SolenoidValve1 50

//Micro Switches for interlocks
#define MicroSwitch1 30

// Communication Variables:
char deviceId[37];
bool deviceIdentified = false;
String inputCommand;

bool solenoidValve = LOW; // For testing purpose only.

bool microSwitch = LOW;

void setup()   { 
  // Initialise the Arduino data pins for OUTPUT

  pinMode(SolenoidValve1, OUTPUT);  // Solenoid Valve.
  pinMode(MicroSwitch1, INPUT);   // Microswitch.
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
  if (solenoidValve) {
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
  
  microSwitch = digitalRead(MicroSwitch1);

  // GUI Communication.
  
  if (Serial.available()) {
    
    //  inputCommand = Serial.readString();
    inputCommand = get_serial_data();
    
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
  
      else if (header == "micro_switch_1") {
        Serial.print("output:micro_switch_1=");
        Serial.println(microSwitch);
        //Serial.println(random(500));
      }
      else if (header == "flow_meter_1") {
        Serial.print("output:flow_meter_1=");
        //Serial.println(flow_sensor1_freq_write, DEC);
        Serial.println(random(100) - random(100));
      }
    }
    else if (keyword == "set") {  
      if (header == "identified") {
        if (value == "1") {
          deviceIdentified = true;
        }
      }
      else if (header == "solenoid_valve_1") {
        if (value == "1") {
          if (digitalRead(SolenoidValve1) == LOW) {
            digitalWrite(SolenoidValve1, HIGH);

            solenoidValve = HIGH; // For testing purpose only.
            
            Serial.println("assigned:solenoid_valve_1=HIGH");
          }
        }
        else {
          digitalWrite(SolenoidValve1, LOW);

          solenoidValve = LOW;  // For testing purpose only.
          
          Serial.println("assigned:solenoid_valve_1=LOW");
        } 
       }

       }
     //Serial.println("assigned:" + header + "=" + value);
    }
  }



