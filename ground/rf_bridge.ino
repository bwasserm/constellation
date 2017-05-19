#include <SoftwareSerial.h>

#define BAUD_RATE 115200

SoftwareSerial radio(2, 3); // RX, TX

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(BAUD_RATE);
  //while (!Serial) {
  // ; // wait for serial port to connect. Needed for native USB port only
  //}

  // set the data rate for the SoftwareSerial port
  radio.begin(BAUD_RATE);
}

void loop() { // run over and over
  if (radio.available()) {
    Serial.write(radio.read());
  }
  if (Serial.available()) {
    radio.write(Serial.read());
  }
}