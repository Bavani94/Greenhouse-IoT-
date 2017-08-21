from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import spidev
import time
from datetime import datetime
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import Adafruit_DHT
import pyrebase
import logging
import json
import RPi.GPIO as GPIO

count = 0

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Configure Cloudinary
cloudinary.config(
  cloud_name = "iotca2",
  api_key = "732475871262856",
  api_secret = "XbjpVSAgUc_PypzoipnXkHyPmG0"
)

# Configure Firebase
pyrebase_config = {
  "apiKey": " AIzaSyAlX8g6Ot35en0SAlY5LPP3DdMFD8ObG50",
  "authDomain": "iotca2-7591e.firebaseapp.com",
  "databaseURL": "https://iotca2-7591e.firebaseio.com",
  "storageBucket": "iotca2-7591e.appspot.com",
  "serviceAccount": "iotca2-7591e-firebase-adminsdk-e7sbb-19bff1dd8e.json"
}

pyrebaseDatabase = pyrebase.initialize_app(pyrebase_config)
db = pyrebaseDatabase.database()
duration = db.child("fan_status").child("duration").get().val()
threshold = db.child("fan_status").child("threshold").get().val()

#Configure MQTT
host = "a2g49f96gkk39l.iot.ap-southeast-1.amazonaws.com"
rootCApath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

def customCallback(client, userdata, message):
  global duration
  global threshold
  global count
  count = 0
  print("Received new message: ")
  print(message.payload)
  #pump_config = json.loads(message.payload)
  #duration = pump_config['duration']
  #threshold = pump_config['threshold']
  print("From topic:")
  print(message.topic)
  print("----------------------")

rpi = AWSIoTMQTTClient("temphum")
rpi.configureEndpoint(host, 8883)
rpi.configureCredentials(rootCApath, privateKeyPath, certificatePath)
rpi.configureOfflinePublishQueueing(-1)
rpi.configureDrainingFrequency(2)
rpi.configureConnectDisconnectTimeout(10)
rpi.configureMQTTOperationTimeout(5)
rpi.connect()
rpi.subscribe("sensors/temphumconfig", 1, customCallback)

# Configure GPIO
relay_pin = 21
dht11_pin = 19

# Main loop - read raw data and display
while True:
   global count
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(relay_pin, GPIO.OUT)
   GPIO.output(relay_pin, GPIO.HIGH)
   print("Relay Pin is now set to HIGH")
   humidity, temperature = Adafruit_DHT.read_retry(11, dht11_pin)
   print(humidity)
   print(temperature)
   print ("Temperature: " + str(temperature) + " Humidity: " + str(humidity))

   if (int(humidity) > threshold):  
       GPIO.output(relay_pin, GPIO.LOW)
       count += 1
       print("Relay is now turning on.")
       time.sleep(duration)
       print("Relay is now off.")
   else:
       GPIO.output(relay_pin, GPIO.LOW)
       count += 1

   data = { 'timestamp': int(time.time()), 'temperature': int(temperature), 'humidity': int(humidity)}
   # result = db.child("temperature_humidity_readings").push(data)
   json_string = json.dumps(data)
   print("Publishing to AWS MQTT Broker...")
   rpi.publish("sensors/temphum", json_string, 1)
   print("Done publishing to AWS MQTT Broker.")
   time.sleep(1)
   if (count == 1):
     GPIO.cleanup()
   