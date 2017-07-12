#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>
// #include <WiFiUdp.h>
#include <ESP8266WiFi.h>
#include "E131/E131.h"

#ifdef __AVR__
  #include <avr/power.h>
#endif

#define NODE_INDEX 1
#define MAX_NUM_NODES 16
#define UNIVERSE 1


/* ESP8266 Only code */

const char* ssid     = "Constellation";
const char* password = "constellation";

const int NODE_PORT = 17227;  // DATE OF THE PARTY TO END ALL PARTIES

#define LED_PIN 2
#define WIFI


#if defined (__AVR_ATtiny85__)
  if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
#endif

// Constellation packet constants
#define HEADER_SIZE 7
char HEADER[HEADER_SIZE] = {'C', 'O', 'N', 'S', 'T', 'E', 'L'};
#define FOOTER_SIZE 6
char FOOTER[FOOTER_SIZE] = {'L', 'A', 'T', 'I', 'O', 'N'};

#define RED_OFFSET 0
#define GREEN_OFFSET 1
#define BLUE_OFFSET 2
#define ALPHA_OFFSET 3

#define APPLY_GAMMA 1
#define LEDS_PER_NODE 2

#define DEBUG_LED 1

char UNSAFE[4] = {'I', '\'', 'm', 'S'};
char ARMED[4] = {'o', 'r', 'r', 'y'};
char BOOM[4] = {'D', 'a', 'v', 'e'};

// I'm afraid I can't do that
#define BOOM_PIN 0
char SAFE[4];

char *boom_state = SAFE;

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

#define PIXEL_OFFSET (4 * (NODE_INDEX))

// Num pixels, pin, pixel type
Adafruit_NeoPixel led = Adafruit_NeoPixel(2, LED_PIN, NEO_GRB + NEO_KHZ800);
E131 e131;

typedef struct led_t{
  char red;
  char green;
  char blue;
  char alpha;
} led_t;

void check_firing_code(char red, char green, char blue, char alpha) {
  if((boom_state == SAFE || boom_state == UNSAFE) &&
      red == UNSAFE[0] && green == UNSAFE[1] &&
      blue == UNSAFE[2] && alpha == UNSAFE[3]) {
        boom_state = UNSAFE;

        Serial.println("Got to UNSAFE");
  }else if((boom_state == UNSAFE || boom_state == ARMED) &&
      red == ARMED[0] && green == ARMED[1] &&
      blue == ARMED[2] && alpha == ARMED[3]){
        boom_state = ARMED;

        Serial.println("Got to ARMED");
  }else if((boom_state == ARMED || boom_state == BOOM) &&
      red == BOOM[0] && green == BOOM[1] &&
      blue == BOOM[2] && alpha == BOOM[3]){
        boom_state = BOOM;
        digitalWrite(BOOM_PIN, LOW);
        delay(100);
        digitalWrite(BOOM_PIN, HIGH);   
        Serial.println("Got to BOOM");
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

//Debugging blink function 
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

  e131.beginMulticast(ssid, password, 1);  /* via Multicast for Universe 1 */

  WiFi.setOutputPower(0);

  Serial.write("Connecting to wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    blink();
    set_leds(255, 0, 0, 0);
    delay(400);
    set_leds(0, 255, 0, 0);
    blink();
    Serial.write("Connecting to wifi...");
  }
  Serial.write("Connected to wifi");
  set_leds(0, 0, 255, 0);

}

void loop() {

    /* Parse a packet and update pixels */
    if(e131.parsePacket()) {
        if (e131.universe == UNIVERSE) {
            set_leds(e131.data[PIXEL_OFFSET + RED_OFFSET],
                     e131.data[PIXEL_OFFSET + GREEN_OFFSET],
                     e131.data[PIXEL_OFFSET + BLUE_OFFSET],
                     e131.data[PIXEL_OFFSET + ALPHA_OFFSET]);
        }
    }
}
