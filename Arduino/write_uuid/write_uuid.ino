#include <EEPROM.h>

char id[] = "52d0536f-575e-4861-96c4-b53fc9710170";  // UUID4. One way of obtaining this is to do "import uuid;  uuid.uuid4()" in a python console.

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i=0; i < 36; i++) {
    EEPROM.write(i, id[i]);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
