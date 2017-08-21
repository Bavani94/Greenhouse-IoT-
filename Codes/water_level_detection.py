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

#Configure MQTT
host = "a2g49f96gkk39l.iot.ap-southeast-1.amazonaws.com"
rootCApath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

rpi = AWSIoTMQTTClient("basicPubSub")
rpi.configureEndpoint(host, 8883)
rpi.configureCredentials(rootCApath, privateKeyPath, certificatePath)
rpi.configureOfflinePublishQueueing(-1)
rpi.configureDrainingFrequency(2)
rpi.configureConnectDisconnectTimeout(10)
rpi.configureMQTTOperationTimeout(5)
rpi.connect()

# Configure GPIO
water_level_pin = 25
buzzer_pin = 17

# Main loop - read raw data and display
while True:
   global count
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(water_level_pin, GPIO.IN)
   GPIO.setup(buzzer_pin, GPIO.OUT)   
   GPIO.output(buzzer_pin, GPIO.LOW) 
   water_level = GPIO.input(water_level_pin)
   print (water_level)

   if (water_level == 0):
       GPIO.output(buzzer_pin, GPIO.HIGH)
       count += 1
       time.sleep(5)
   else:
       GPIO.output(buzzer_pin, GPIO.LOW)
       count += 1
       
   data = { 'timestamp': int(time.time()), 'water_level': water_level}
   # result = db.child("water_level").push(data)
   json_string = json.dumps(data)
   print("Publishing to AWS MQTT Broker...")
   rpi.publish("sensors/waterlevel", json_string, 1)
   print("Done publishing to AWS MQTT Broker.")
   time.sleep(5)
   if (count == 1):
     GPIO.cleanup()
   