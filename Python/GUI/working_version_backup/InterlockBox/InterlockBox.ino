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

// Flow meters. x5.
const int flowSensorPins[] = {3, 2, 18, 19, 20};
volatile int flowSensorFreqs[] = {0, 0, 0, 0, 0};
int flowSensorFreqsWrite[] = {0, 0, 0, 0, 0};

// Solenoid Valve Variables. x5.
const int solenoidValvePins[] = {13, 31}; // Make this 30, 31. 13 is for the in-built LED and so is for testing purpose only.
bool solenoidValveValues[] = {LOW, LOW};

// Micro Switches for interlocks. x2.
const int microSwitchPins[] = {28, 29}; 
bool microSwitchValues[] = {LOW, LOW};

// Vacuum Valves. x2.
const int vacuumValvePins[] = {36, 37, 38, 39};
bool vacuumValveMicroSwitchValues[] = {LOW, LOW, LOW, LOW};
bool vacuumValveValues[] = {LOW, LOW};  // For each vacuum valve, two microswitches determine whether or not it's open.

// Communication Variables:
char deviceId[37];
bool deviceIdentified = false;
String inputCommand;


void setup()   { 
  // Initialise the Arduino data pins.

  // Solenoid Valves.
  for (unsigned i = 0; i < sizeof(solenoidValvePins) / sizeof(int); i++) {
    pinMode(solenoidValvePins[i], OUTPUT);
  }

  // Flow Meters.
  for (unsigned i = 0; i < sizeof(flowSensorPins) / sizeof(int); i++) {
    pinMode(flowSensorPins[i], INPUT);
  }
  
  // Vacuum Valves.
  for (unsigned i = 0; i < sizeof(vacuumValvePins) / sizeof(int); i++) {
    pinMode(vacuumValvePins[i], INPUT);
  }
  
  // Microswitches.
  for (unsigned i = 0; i < sizeof(microSwitchPins) / sizeof(int); i++) {
    pinMode(microSwitchPins[i], INPUT);
  }
  
  pinMode(13, OUTPUT);  // Inbuilt LED.
  
  Serial.begin(115200);

  // Get this Arduino's device ID from memory.
  for (int i=0; i < 36; i++) {
    deviceId[i] = EEPROM.read(i);
  }

  // Interrupts for flow sensors.
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[0]), flow_interrupt0, RISING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[1]), flow_interrupt1, RISING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[2]), flow_interrupt2, RISING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[3]), flow_interrupt3, RISING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[4]), flow_interrupt4, RISING);
  
}

void flow_interrupt0() {
  flowSensorFreqs[0]++;
}

void flow_interrupt1() {
  flowSensorFreqs[1]++;
}

void flow_interrupt2() {
  flowSensorFreqs[2]++;
}

void flow_interrupt3() {
  flowSensorFreqs[3]++;
}

void flow_interrupt4() {
  flowSensorFreqs[4]++;
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
  
  
  // Read Flow Meters.
  
  currentTime = millis();
  // Every second, calculate and print litres/hour
  if(currentTime >= (cloopTime + 1000)) {
    cloopTime = currentTime; // Updates cloopTime
    for (unsigned i = 0; i < sizeof(flowSensorPins) / sizeof(int); i++) {
      flowSensorFreqsWrite[i] = flowSensorFreqs[i]; //
      flowSensorFreqs[i] = 0; // Reset counter.
    }
  }

  // Read Vacuum Valves.
  for (unsigned i = 0; i < sizeof(vacuumValvePins) / sizeof(int); i++) {
    vacuumValveMicroSwitchValues[i] = digitalRead(vacuumValvePins[i]);
  }

  // Determine whether each of the two vacuum valves are open or not based on the 4 microswitch values.
  // Whether or not a vacuum valve is open depends on the values of two of its associated microswitches.
  
  for (unsigned i = 0; i < sizeof(vacuumValvePins) / sizeof(int) - 1; i++) {
    if ( (vacuumValveMicroSwitchValues[i]) & ( ! vacuumValveMicroSwitchValues[i + 1] ) ) {
      // Valve is closed.
      vacuumValveValues[((int) (i / 2))] = LOW;
    }
    else if ( ( ! vacuumValveMicroSwitchValues[i]) & (vacuumValveMicroSwitchValues[i + 1] ) ) {
      // Valve is open.
      vacuumValveValues[((int) (i / 2))] = HIGH;
    }
    else {
      // Error State.
    }
  }
  
  // Read Micro Switches.
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

    String filteredHeader;
    if (serialNumberCharacterIndex > -1) {
      filteredHeader = header.substring(0, serialNumberCharacterIndex);
    }
    else {
      filteredHeader = header;
    }

    if (keyword == "query") {
      if (filteredHeader == "identification") {
        Serial.print("output:device_id=");
        Serial.println(deviceId);
      }
      else if (filteredHeader == "micro_switch") {
        if (serialNumber.toInt() <= (sizeof(microSwitchPins) / sizeof(int))) {
          Serial.print("output:micro_switch#" + serialNumber + "=");
          Serial.println(microSwitchValues[serialNumber.toInt() - 1]);  // We need to subtract 1 because array counting starts from 0 whereas our label counters (micro_switch#1) start from 1.
        }
      }
      else if (filteredHeader == "flow_meter") {
        if (serialNumber.toInt() <= (sizeof(flowSensorPins) / sizeof(int))) {
          Serial.print("output:flow_meter#"  + serialNumber + "=");  
          //Serial.println(flowSensorFreqsWrite[serialNumber.toInt() - 1], DEC);
          Serial.println(random(100) - random(100));
        } 
      }
      else if (filteredHeader == "vacuum_valve") {
        if (serialNumber.toInt() <= sizeof(vacuumValveValues) / sizeof(bool)) {
          Serial.print("output:vacuum_valve#" + serialNumber + "=");
          Serial.println(vacuumValveValues[serialNumber.toInt() - 1]);
        }
      }
    }
    else if (keyword == "set") {
      
      if (filteredHeader == "identified") {
        if (value == "1") {
          deviceIdentified = true;
        }
      }
      else if (filteredHeader == "solenoid_valve") {
        if (value == "1") {
          if (digitalRead(solenoidValvePins[serialNumber.toInt() - 1]) == LOW) {
            digitalWrite(solenoidValvePins[serialNumber.toInt() - 1], HIGH);   
            solenoidValveValues[serialNumber.toInt() - 1] = HIGH;   
            Serial.println("assigned:solenoid_valve#" + serialNumber + "=1");
          }
        }
        else {
          digitalWrite(solenoidValvePins[serialNumber.toInt() - 1], LOW);        
          solenoidValveValues[serialNumber.toInt() - 1] = LOW;   
          Serial.println("assigned:solenoid_valve#" + serialNumber + "=0");
        }
      
      }
    }
  }
}



