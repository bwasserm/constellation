#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>
#include <WiFiUdp.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

/* ESP8266 Only code */
#ifdef ESP8266

#include <ESP8266WiFi.h>

const char* ssid     = "FortKnox";
const char* password = "Golden.Finger.Golden.Finger";

const int NODE_PORT = 17227;  // DATE OF THE PARTY TO END ALL PARTIES

#define LED_PIN 2
#define WIFI
#endif /* End of ESP8266 Only code */

#if defined (__AVR_ATtiny85__)
  if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
#endif

#ifndef WIFI
  #define RF
#endif

#ifdef RF
#define RF_BAUD_RATE 115200
#endif

// Constellation packet constants
#define MAX_NUM_NODES 16
#define HEADER "CONSTEL"
#define HEADER_SIZE strlen(HEADER)
#define FOOTER "LATION"
#define FOOTER_SIZE strlen(FOOTER)
// Packet = CONSTEL[pixels:rgb]LATION
#define PACKET_LEN ((HEADER_SIZE) + 4 * (MAX_NUM_NODES) + FOOTER_SIZE)
#define BUFFER_SIZE (2 * (PACKET_LEN))
#define RED_OFFSET 0
#define GREEN_OFFSET 1
#define BLUE_OFFSET 2
#define IGNITER_OFFSET 4

byte neopix_gamma[] = {
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 };

// UPDATE ME FOR EACH NODE
#define NODE_INDEX 0
#define PIXEL_OFFSET ((HEADER_SIZE) + 4 * (NODE_INDEX))

// RF Module setup
SoftwareSerial radio(2, 3); // RX, TX  NO LONGER TRUE, USES SPI INSTEAD


// Num pixels, pin, pixel type
Adafruit_NeoPixel led = Adafruit_NeoPixel(2, LED_PIN, NEO_GRB + NEO_KHZ800);
WiFiUDP Udp;
  
char buffer[BUFFER_SIZE];
int buf_index = 0;

void setup() {
  radio.begin(RF_BAUD_RATE);
  led.begin();
  led.show();

  memset(buffer, 0, BUFFER_SIZE);

  WiFi.begin(ssid, password);

  #ifdef WIFI
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Udp.begin(NODE_PORT);
  #endif
}

void loop() {

  #ifdef RF
  // Read packets in off the radio
  while(radio.available()){
    buffer[buf_index] = radio.read();
    buf_index += 1;
    if(buf_index >= BUFFER_SIZE){
    	buf_index = 0;
    }
    if(buf_index > 1 && buffer[buf_index-2] == 'N'){
    	break;
    }
  }
  #endif

  #ifdef WIFI
  // Read packets from the UDP socket
  while(Udp.parsePacket()){
    Udp.read(&(buffer[buf_index]), 1);
    buf_index += 1;
    if(buf_index >= BUFFER_SIZE){
      buf_index = 0;
    }
    if(buf_index > 1 && buffer[buf_index-2] == 'N'){
      break;
    }
  }
  #endif

  // Find the packet in the buffer
  char *pkt = strstr(buffer, HEADER);
  char *footer = strstr(buffer, FOOTER);
  int payload_len = int(footer) - int(pkt);
  // If a valid packet was received
  if(pkt != NULL && footer != NULL && payload_len == (PACKET_LEN - FOOTER_SIZE)){
    char red = pkt[PIXEL_OFFSET + RED_OFFSET];
    char green = pkt[PIXEL_OFFSET + GREEN_OFFSET];
    char blue = pkt[PIXEL_OFFSET + BLUE_OFFSET];
    // Set LED
    led.setPixelColor(0, red, green, blue);
    led.setPixelColor(1, red, green, blue);
    led.show();
    buf_index = 0;
  }
}
