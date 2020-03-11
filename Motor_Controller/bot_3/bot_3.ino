#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

WiFiClient bot3;

WiFiUDP UDPServer;


////////////////////////////////GLOBAL VARIABLES/////////////////////////////////////
//Motor A
const int inputPin1  = 12;    // Pin 15 of L293D IC, D1 Pin of NodeMCU
const int inputPin2  = 14;     // Pin 10 of L293D IC, D0 Pin of NodeMCU
int EN1 = 5;                 // Pin 01 of L293D IC, D6 Pin of NodeMCU

//Motor B
const int inputPin3  = 15;     // Pin 07 of L293D IC, D2 Pin of NodeMCU
const int inputPin4  = 13;     // Pin 02 of L293D IC, D3 Pin of NodeMCU
int EN2 = 4;                 // Pin 09 of L293D IC, D5 Pin of NodeMCU

const char* ssid = "WiFi";
const char* password = "limca1234567890";
//Static IP address configuration
IPAddress staticIP(192, 168, 0, 133); //ESP static ip, keep format 192,168,0,13X
IPAddress gateway(192, 168, 0, 1);   //IP Address of your WiFi Router (Gateway)
IPAddress subnet(255, 255, 255, 0);  //Subnet mask
IPAddress dns(8, 8, 8, 8);  //DNS
 
 
const char* deviceName = "bot3";

String udpdata = "0,0,0,0";
unsigned int UDPPort = 2801;

//Packet Buffer
const int packetSize = 15;
byte packetBuffer[packetSize];

unsigned long time_since_last_msg;

/////////////////////////////////////// MOTOR PROTOTYPE////////////////////////////////
class MotorOutput { 
   private:
   
    int inputP1;
    int inputP2;
    int Enable; 

   public:
    
    MotorOutput(int IP1, int IP2, int En) {
    pinMode(En, OUTPUT);
    pinMode(IP1, OUTPUT);
    pinMode(IP2, OUTPUT);
    inputP1 = IP1;
    inputP2 = IP2;
    Enable = En;
   }

   void forward() {
    digitalWrite(inputP1, HIGH);
    digitalWrite(inputP2, LOW);
   }

   void backward() {
    digitalWrite(inputP1, LOW);
    digitalWrite(inputP2, HIGH);
   }

   void speed(int pwm) {
    analogWrite(Enable, pwm);//sets the motors speed
   }
};
///////////////////////////////////HEARTBEAT CHECK///////////////////////////////////
bool heartbeat_check(unsigned long time_since_last_msg) {
  unsigned long new_msg = millis();
  //if no message is recieved in last one second, report false
  if (new_msg - time_since_last_msg >= 1000) {
    return false; 
  }
  return true; 
}
///////////////////////////////////UDP///////////////////////////////////////////////
void handleUDPServer() {
  int cb = UDPServer.parsePacket();
  if (cb) {
    UDPServer.read(packetBuffer, packetSize);
    udpdata = "";
    for(int i = 0; i < packetSize; i++) {
      udpdata += (char)packetBuffer[i];
    } 
    
    time_since_last_msg = millis();
  }
}

///////////////////////////////////WIFI//////////////////////////////////////////////

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.hostname(deviceName);      // DHCP Hostname (useful for finding device for static lease)
  WiFi.config(staticIP, subnet, gateway, dns);
  WiFi.begin(ssid, password);

  WiFi.mode(WIFI_STA); //WiFi mode station (connect to wifi router only  

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

////////////////////////////////NEW OBJECTS/////////////////////////////////////////
MotorOutput *rightmotor;
MotorOutput *leftmotor;

/////////////////////////////////////////////////////////////////////////////////////////////////
void setup() {   
  Serial.begin(9600);
   setup_wifi();
   UDPServer.begin(UDPPort); 

   rightmotor = new MotorOutput(inputPin1,inputPin2,EN1);
   leftmotor = new MotorOutput(inputPin3,inputPin4,EN2);
   
 }

void loop() { 
  handleUDPServer();    
  char str[udpdata.length()];
  
  for (int i = 0; i < sizeof(str); i++) { 
    str[i] = udpdata[i];
    }
    
    char *token = strtok(str, ","); 
    // Keep printing tokens while one of the 
    // delimiters present in str[]. 
    int j = 0;
    int split_msg[4];
    while (token != NULL) { 
        split_msg[j]=atoi(token); 
        token = strtok(NULL, ",");
        j++; 
    }    
    
  bool rightdirection = split_msg[0]; 
  bool leftdirection =  split_msg[2];
  int  rightspeed =     split_msg[1]; 
  int  leftspeed =      split_msg[3];
  
  // unhealthy signal
  if (!heartbeat_check(time_since_last_msg)) {
    rightdirection = 1;
    leftdirection =  1;
    rightspeed =     0;
    leftspeed =      0;
  }
  
  //debugging
  Serial.println("right direction");
  Serial.println(rightdirection);
  Serial.println("right speed");
  Serial.println(rightspeed);
  Serial.println("left direction");
  Serial.println(leftdirection);
  Serial.println("left speed");
  Serial.println(leftspeed);
           
  if(rightdirection) {
    rightmotor->forward();
   }
  else {
    rightmotor->backward();
   }
  if(leftdirection) {
    leftmotor->forward();
   }
  else {
    leftmotor->backward();
   }
   
   rightmotor->speed(rightspeed);
   leftmotor->speed(leftspeed);        
}
