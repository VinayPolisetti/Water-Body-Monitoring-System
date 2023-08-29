#include <BoltDeviceCredentials.h>
#include <BoltIoT-Arduino-Helper.h>
#include <ThingSpeak.h>
#include<LiquidCrystal.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 13
LiquidCrystal lcd(2,3,4,5,6,7);
   
const int in=8;
const int out=9;
const int green=10;
const int orange=11;
const int red=12;
float calibration_value = 22.34 - 1.2;
int phval = 0; 
unsigned long int avgval; 
int buffer_arr[10],temp;
float ph_act;
int turbidity;

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

float Celcius=0;
 
void setup(){
Serial.begin(9600);
lcd.begin(16,2);
pinMode(in, INPUT);
pinMode(out, OUTPUT);
pinMode(green, OUTPUT);
pinMode(orange, OUTPUT);
pinMode(red, OUTPUT);
digitalWrite(green,LOW);
digitalWrite(orange,LOW);
digitalWrite(red,LOW);
sensors.begin();
lcd.setCursor(0,0);
lcd.print("Flood Monitoring");
lcd.setCursor(0,1);
lcd.print("Alerting System");
delay(1000);
lcd.clear();
}

void loop()
{
float dur;
float dist;
float per;  
for(int i=0;i<10;i++) 
 { 
 buffer_arr[i]=analogRead(A0);
 delay(30);
 }
 for(int i=0;i<9;i++)
 {
 for(int j=i+1;j<10;j++)
 {
 if(buffer_arr[i]>buffer_arr[j])
 {
 temp=buffer_arr[i];
 buffer_arr[i]=buffer_arr[j];
 buffer_arr[j]=temp;
 }
 }
 }
 avgval=0;
 for(int i=2;i<8;i++)
 avgval+=buffer_arr[i];
 float volt=(float)avgval*5.0/1024/6; 
  ph_act = -5.70 * volt + calibration_value;
  turbidity = analogRead(A1);
  turbidity = map(turbidity, 0,640, 100, 0);
  if(turbidity<0)
  {
    turbidity = 0;
  }
digitalWrite(out,LOW);
delayMicroseconds(2);
digitalWrite(out,HIGH);
delayMicroseconds(10);
digitalWrite(out,LOW);
dur=pulseIn(in,HIGH);
dist=(dur*0.034)/2;
per=100*(9.6-dist)/6.5;
if(per<0)
{
  per=0;
}
if(per>100)
{
  per=100;
}
sensors.requestTemperatures(); 
Celcius=sensors.getTempCByIndex(0);
Serial.println(float(per));
Serial.println(ph_act);
Serial.println(turbidity);
Serial.println(Celcius);
lcd.setCursor(0,0);
lcd.print("Water Level:");
lcd.print(String(per));
lcd.print("%  ");
if(per>=80)       
{
  lcd.setCursor(0,1);
  lcd.print("Red Alert!   ");
  digitalWrite(red,HIGH);
  digitalWrite(green,LOW);
  digitalWrite(orange,LOW);
}
else if(per>=55)    
{
  lcd.setCursor(0,1);
  lcd.print("Orange Alert!  ");
  digitalWrite(orange,HIGH);
  digitalWrite(red,LOW);
  digitalWrite(green,LOW);
  
}else          
{
 lcd.setCursor(0,1);
 lcd.print("Green Alert!  ");
 digitalWrite(green,HIGH); 
 digitalWrite(orange,LOW);
 digitalWrite(red,LOW);
}
delay(30000);
}
