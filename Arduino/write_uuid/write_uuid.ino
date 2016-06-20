#include <EEPROM.h>

char id[] = "41b70a36-a206-41c5-b743-1e5b8429b9a1";  // UUID4. One way of obtaining this is to do "import uuid;  uuid.uuid4()" in a python console.

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
