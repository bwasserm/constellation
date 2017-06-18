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
#define HEADER_SIZE 7
char HEADER[HEADER_SIZE] = {'C', 'O', 'N', 'S', 'T', 'E', 'L'};
#define FOOTER_SIZE 6
char FOOTER[FOOTER_SIZE] = {'L', 'A', 'T', 'I', 'O', 'N'};
// Packet = CONSTEL[pixels:rgb]LATION
#define PACKET_LEN ((HEADER_SIZE) + 4 * (MAX_NUM_NODES) + FOOTER_SIZE)
#define BUFFER_SIZE (5 * (PACKET_LEN))
#define RED_OFFSET 0
#define GREEN_OFFSET 1
#define BLUE_OFFSET 2
#define ALPHA_OFFSET 3

#define APPLY_GAMMA 1
#define LEDS_PER_NODE 2

#define DEBUG_LED 1

char BOOM3[4] = {'I', '\'', 'm', 'S'};
char BOOM2[4] = {'o', 'r', 'r', 'y'};
char BOOM1[4] = {'D', 'a', 'v', 'e'};
// I'm afraid I can't do that
#define BOOM_PIN 2
#define SAFE 3
#define UNSAFE 2
#define ARMED 1
#define BOOM 0

char boom_state = SAFE;

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
#define NODE_INDEX 1
#define PIXEL_OFFSET ((HEADER_SIZE) + 4 * (NODE_INDEX))

// RF Module setup
#ifdef RF
SoftwareSerial radio(2, 3); // RX, TX  NO LONGER TRUE, USES SPI INSTEAD
#endif

// Num pixels, pin, pixel type
Adafruit_NeoPixel led = Adafruit_NeoPixel(2, LED_PIN, NEO_GRB + NEO_KHZ800);
WiFiUDP Udp;
  
char myBuffer[BUFFER_SIZE];
int buf_index = 0;
int counter = 0;

typedef struct led_t{
  char red;
  char green;
  char blue;
  char alpha;
} led_t;

int read_buffer(led_t* setpoint){
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
  int myPacketSize = 0;
  while(1) {
    myPacketSize = Udp.parsePacket();
    if(myPacketSize)
    {
      Serial.print("Received packet of size:");
      Serial.println(myPacketSize);
      
      Udp.read(myBuffer, myPacketSize);
      
      Serial.print("Contents:");
      Serial.println(myBuffer);
      counter+=1;
      Serial.print("Counter:");
      Serial.println(counter);
      break;
      }
    }
  
  
  #endif

  // Find the packet in the buffer
  char *pkt = myBuffer;
  /*
  strstr(myBuffer, HEADER);
  Serial.print("Header: " );
  Serial.println(pkt);
  Serial.print("Int of Packet: ");
  Serial.println(int(pkt));
  */
  
  // If a valid packet was received
  if(myPacketSize == PACKET_LEN){
    setpoint->red = pkt[PIXEL_OFFSET + RED_OFFSET];
    setpoint->green = pkt[PIXEL_OFFSET + GREEN_OFFSET];
    setpoint->blue = pkt[PIXEL_OFFSET + BLUE_OFFSET];
    setpoint->alpha = pkt[PIXEL_OFFSET + ALPHA_OFFSET];
    buf_index = 0;
    Serial.println("Got Milk");
    return 1; // Got packet
  }
  else{
    return 0; // No packet yet
  }
}

void check_firing_code(char red, char green, char blue, char alpha){
  if((boom_state == SAFE || boom_state == UNSAFE) &&
      red == BOOM3[0] && green == BOOM3[1] &&
      blue == BOOM3[2] && alpha == BOOM3[3]){
        boom_state == UNSAFE;
  }else if((boom_state == UNSAFE || boom_state == ARMED) &&
      red == BOOM2[0] && green == BOOM2[1] &&
      blue == BOOM2[2] && alpha == BOOM2[3]){
        boom_state == ARMED;
  }else if((boom_state == ARMED || boom_state == BOOM) &&
      red == BOOM1[0] && green == BOOM1[1] &&
      blue == BOOM1[2] && alpha == BOOM1[3]){
        boom_state == BOOM;
  }else{
    boom_state = SAFE;
  }
}

void set_leds(led_t setpoint){
  char red = setpoint.red;
  char green = setpoint.green;
  char blue = setpoint.blue;
  char alpha = setpoint.alpha;

  set_leds(red, green, blue, alpha);
}

void set_leds(char red, char green, char blue, char alpha){

  check_firing_code(red, green, blue, alpha);

  if(boom_state == SAFE){
    if(APPLY_GAMMA){
      red = neopix_gamma[red];
      green = neopix_gamma[green];
      blue = neopix_gamma[blue];
    }
    for(char i=0; i < LEDS_PER_NODE; i++){
      led.setPixelColor(i, red, green, blue);
    }
    led.show();
  }

  if(boom_state == BOOM){
    digitalWrite(BOOM_PIN, 0);
  }
}

int led_state = 0;

void blink(){
  digitalWrite(LED_BUILTIN, led_state);
  led_state = !led_state;
}

void setup() {
  pinMode(BOOM_PIN, OUTPUT);
  digitalWrite(BOOM_PIN, HIGH);  // Active Low
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(115200);
  
  led.begin();
  led.show();

  set_leds(128, 0, 0, 0);

  memset(myBuffer, 0, BUFFER_SIZE);

  IPAddress ip(192, 168, 0, NODE_INDEX);
  IPAddress gateway(192, 168, 0, 1);
  IPAddress subnet(255, 255, 255, 0);
  //WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, password);

  #ifdef WIFI
  Serial.write("Connecting to wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    blink();
    set_leds(128, 0, 0, 0);
    delay(400);
    set_leds(255, 0, 0, 0);
    blink();
    Serial.write("Connecting to wifi...");
  }
  Serial.write("Connected to wifi");
  Udp.begin(NODE_PORT);
  #endif

  blink();
  delay(1000);
  blink();
  delay(1000);
  blink();
  delay(1000);
  blink();
  delay(1000);
  blink();
  delay(1000);
  blink();
}

void loop() {

    led_t setpoint;
    //set_leds(0, 128, 0, 0);
    blink();
    if(read_buffer(&setpoint)){
      //set_leds(0, 0, 128, 0);
      blink();
      // Set LED
      set_leds(setpoint);
    }
    //set_leds(0, 255, 0, 0);
}
