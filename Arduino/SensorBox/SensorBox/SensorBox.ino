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
#include <MAX31856.h>

// Flow meters. x5.
const int flowSensorPins[] = {18, 19, 20, 3, 2};
volatile int flowSensorFreqs[] = {0, 0, 0, 0, 0};
float flowSensorFreqsWrite[] = {0.0, 0.0, 0.0, 0.0, 0.0};
unsigned long currentTime;
unsigned long cloopTime;

// Temperature Sensors. 8x.
// The power requirement for the board is less than 2mA.  Most microcontrollers can source or sink a lot more
// than that one each I/O pin.  For example, the ATmega328 supports up to 20mA.  So it is possible to power the
// board using I/O pins for power - so you can turn the board on and off (if you want to).
// FAULT and DRDY are not used by the library (see above)
#define SCK1    44
#define SDI1    42
#define SDO1    40

#define SCK2    49
#define SDI2    51
#define SDO2    53

#define CS1    46
#define CS2    48
#define CS3    50
#define CS4    52
#define CS5    47
#define CS6    45
#define CS7    43
#define CS8    41

// Define pins for error state LED, communication LED
#define LED_ERR 12
#define LED_COM 13

// MAX31856 Initial settings (see MAX31856.h and the MAX31856 datasheet)
// The default noise filter is 60Hz, suitable for the USA
#define CR0_INIT  (CR0_AUTOMATIC_CONVERSION + CR0_OPEN_CIRCUIT_FAULT_TYPE_K /* + CR0_NOISE_FILTER_50HZ */)
#define CR1_INIT  (CR1_AVERAGE_2_SAMPLES + CR1_THERMOCOUPLE_TYPE_K)
#define MASK_INIT (~(MASK_VOLTAGE_UNDER_OVER_FAULT + MASK_THERMOCOUPLE_OPEN_FAULT))

MAX31856 *temperature1;
MAX31856 *temperature2;
MAX31856 *temperature3;
MAX31856 *temperature4;
MAX31856 *temperature5;
MAX31856 *temperature6;
MAX31856 *temperature7;
//MAX31856 *temperature8;

// Communication Variables:
char deviceId[37];
bool deviceIdentified = false;
String inputCommand;

float t[] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

void setup()   { 
  // Init Com and Error LED's
  pinMode(LED_ERR, OUTPUT);
  pinMode(LED_COM, OUTPUT);
  digitalWrite(LED_COM, LOW);
  digitalWrite(LED_ERR, LOW);
  
  // Flow Meters.
  for (unsigned i = 0; i < sizeof(flowSensorPins) / sizeof(int); i++) {
    pinMode(flowSensorPins[i], INPUT);
  }
    
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

  // Define the pins used to communicate with the MAX31856
  temperature1 = new MAX31856(SDI1, SDO1, CS1, SCK1);
  temperature2 = new MAX31856(SDI1, SDO1, CS2, SCK1);
  temperature3 = new MAX31856(SDI1, SDO1, CS3, SCK1);
  temperature4 = new MAX31856(SDI1, SDO1, CS4, SCK1);
  temperature5 = new MAX31856(SDI2, SDO2, CS5, SCK2);
  temperature6 = new MAX31856(SDI2, SDO2, CS6, SCK2);
  temperature7 = new MAX31856(SDI2, SDO2, CS7, SCK2);
//  temperature8 = new MAX31856(SDI2, SDO2, CS8, SCK2);
  
  // Initializing the MAX31855's registers
  temperature1->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature1->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature1->writeRegister(REGISTER_MASK, MASK_INIT);

  temperature2->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature2->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature2->writeRegister(REGISTER_MASK, MASK_INIT);

  temperature3->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature3->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature3->writeRegister(REGISTER_MASK, MASK_INIT);

  temperature4->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature4->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature4->writeRegister(REGISTER_MASK, MASK_INIT);

  temperature5->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature5->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature5->writeRegister(REGISTER_MASK, MASK_INIT);

  temperature6->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature6->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature6->writeRegister(REGISTER_MASK, MASK_INIT);

  temperature7->writeRegister(REGISTER_CR0, CR0_INIT);
  temperature7->writeRegister(REGISTER_CR1, CR1_INIT);
  temperature7->writeRegister(REGISTER_MASK, MASK_INIT);

//  temperature8->writeRegister(REGISTER_CR0, CR0_INIT);
//  temperature8->writeRegister(REGISTER_CR1, CR1_INIT);
//  temperature8->writeRegister(REGISTER_MASK, MASK_INIT);
  
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

  // Get the current time in milliseconds
  currentTime = millis();
  
  // Every half second, calculate and print litres/hour, and read temperatures
  // The temperatures can be moved into their own if clause to read them 
  // out more often.
  if(currentTime >= (cloopTime + 1000)) {
    
    cloopTime = currentTime; // Updates cloopTime
    // Read Flow Meters.
    
    for (unsigned i = 0; i < sizeof(flowSensorPins) / sizeof(int); i++) {
      flowSensorFreqsWrite[i] = (float)flowSensorFreqs[i] * 0.06; //(1000 pulses per l, 60 s in a min, measuring for 0.5 s)
      flowSensorFreqs[i] = 0; // Reset counter.
    }
    
    // Temperature sensors (read out avery second for now)
    t[0] = temperature1->readThermocouple(CELSIUS);
    t[1] = temperature2->readThermocouple(CELSIUS);
    t[2] = temperature3->readThermocouple(CELSIUS);
    t[3] = temperature4->readThermocouple(CELSIUS);
    t[4] = temperature5->readThermocouple(CELSIUS);
    t[5] = temperature6->readThermocouple(CELSIUS);
    t[6] = temperature7->readThermocouple(CELSIUS);
//    t[7] = temperature8->readThermocouple(CELSIUS);
  }
   
  // GUI Communication.
  digitalWrite(LED_COM, LOW);
  
  if (Serial.available()) {
    
    digitalWrite(LED_COM, HIGH);
    
    // Get the message from the serial port
    inputCommand = get_serial_data();

    // Dissect the message into it's components
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

    // Do stuff with the message components according to the GUI commands
    if (keyword == "query") {
      if (filteredHeader == "identification") {
        Serial.print("output:device_id=");
        Serial.println(deviceId);
      }
      else if (filteredHeader == "flow_meter") {
        if (serialNumber.toInt() <= (sizeof(flowSensorPins) / sizeof(int))) {
          Serial.print("output:flow_meter#"  + serialNumber + "=");  
          Serial.println(flowSensorFreqsWrite[serialNumber.toInt() - 1], 2);
        } 
      }
      else if (filteredHeader == "temp_sensor") {
        if (serialNumber.toInt() <= (sizeof(flowSensorPins) / sizeof(int))) {
          Serial.print("output:temp_sensor#"  + serialNumber + "=");
          Serial.println(t[serialNumber.toInt() - 1], 2);
        } 
      }
    }
    else if (keyword == "set") {
      if (filteredHeader == "identified") {
        if (value == "1") {
          deviceIdentified = true;
        }
      }
    }
  }
}


