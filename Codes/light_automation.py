from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import spidev
import time
from datetime import datetime
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
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
duration = db.child("led_status").child("duration").get().val()
threshold = db.child("led_status").child("threshold").get().val()

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
  print('count resetted to value : ' + str(count))
  print("Received new message: ")
  print(message.payload)
  complete = True
  #pump_config = json.loads(message.payload)
  #duration = pump_config['duration']
  #threshold = pump_config['threshold']
  print("From topic:")
  print(message.topic)
  print("----------------------")

rpi = AWSIoTMQTTClient("light")
rpi.configureEndpoint(host, 8883)
rpi.configureCredentials(rootCApath, privateKeyPath, certificatePath)
rpi.configureOfflinePublishQueueing(-1)
rpi.configureDrainingFrequency(2)
rpi.configureConnectDisconnectTimeout(10)
rpi.configureMQTTOperationTimeout(5)
rpi.connect()
rpi.subscribe("sensors/lightconfig", 1, customCallback)

# Configure GPIO
led_pin = 18

# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
   adc = spi.xfer2([1,(8+channel)<<4,0])
   data = ((adc[1]&3) << 8) + adc[2]
   return data

# Main loop - read raw data and display
while True:
   global count
   print("Subscribed duration: " + str(duration))
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_pin, GPIO.OUT)
   GPIO.output(led_pin, GPIO.LOW)
   light_value = ReadChannel(1)
   print("Light Value: " + str(light_value))
   
   if (light_value > threshold):
     GPIO.output(led_pin, GPIO.HIGH)
     count += 1
     time.sleep(duration)
   else:
     count += 1
     GPIO.output(led_pin, GPIO.LOW)

   data = { 'timestamp': int(time.time()), 'light_value': int(light_value)}
   # result = db.child("light_readings").push(data)
   json_string = json.dumps(data)
   print("Publishing to AWS MQTT Broker.")
   rpi.publish("sensors/light", json_string, 1)
   print("Done publishing to AWS MQTT Broker.")
   time.sleep(1)
   if (count == 1):
     GPIO.cleanup()

   