#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>

#define USING_RF 1
#define USING_WIFI (!(USING_RF))

#define RF_BAUD_RATE 115200
#define MAX_NUM_NODES 100
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
#define LED_PIN 3

// UPDATE ME FOR EACH NODE
#define NODE_INDEX 0
#define PIXEL_OFFSET ((HEADER_SIZE) + 4 * (NODE_INDEX))

SoftwareSerial radio(2, 3); // RX, TX
// Num pixels, pin, pixel type
Adafruit_NeoPixel led = Adafruit_NeoPixel(1, LED_PIN, NEO_GRB + NEO_KHZ800);

char buffer[BUFFER_SIZE];
int buf_index = 0;

void setup() {
  radio.begin(RF_BAUD_RATE);
  led.begin();
  led.show();

  memset(buffer, 0, BUFFER_SIZE);
}

void loop() {

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
    led.show();
    buf_index = 0;
  }
}
