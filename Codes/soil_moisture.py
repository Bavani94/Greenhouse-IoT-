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
duration = db.child("pump_status").child("duration").get().val()
threshold = db.child("pump_status").child("threshold").get().val()

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
  pump_config = json.loads(message.payload)
  # duration = pump_config['duration']
  threshold = int(pump_config['threshold'])
  print("New threshold: " + str(threshold))
  print("From topic:")
  print(message.topic)
  print("----------------------")

rpi = AWSIoTMQTTClient("soil")
rpi.configureEndpoint(host, 8883)
rpi.configureCredentials(rootCApath, privateKeyPath, certificatePath)
rpi.configureOfflinePublishQueueing(-1)
rpi.configureDrainingFrequency(2)
rpi.configureConnectDisconnectTimeout(10)
rpi.configureMQTTOperationTimeout(5)
rpi.connect()
rpi.subscribe("sensors/soilconfig", 1, customCallback)

# Configure GPIO
relay_pin = 20

# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
   adc = spi.xfer2([1,(8+channel)<<4,0])
   data = ((adc[1]&3) << 8) + adc[2]
   return data

# Main loop - read raw data and display
while True:
   global count
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(relay_pin, GPIO.OUT)
   GPIO.output(relay_pin, GPIO.HIGH)
   print("Relay Pin is now set to HIGH")
   moisture_value = ReadChannel(0)
   print("Moisture value taken.")
   moisture_percentage = 100.0000 - (moisture_value / 10.24)
   print("Dryness percentage calculated.")
   print ("Moisture Value: " + str(moisture_value) + " Moisture Percentage: " + str(round(moisture_percentage, 2)) + "%")
   print("Threshold: " + str(threshold))

   if (moisture_percentage < threshold):
       GPIO.output(relay_pin, GPIO.LOW)
       count += 1
       print("Relay is now turning on.")
       time.sleep(duration)
       print("Relay is now off.")
   else:
       GPIO.output(relay_pin, GPIO.HIGH)
       count += 1

   data = { 'timestamp': int(time.time()), 'moisture_value': str(moisture_value), 'moisture_percentage': str(round(moisture_percentage, 2))}
   # result = db.child("soil_moisture_readings").push(data)
   json_string = json.dumps(data)
   print("Publishing to AWS MQTT Broker...")
   rpi.publish("sensors/soil", json_string, 1)
   print("Done publishing to AWS MQTT Broker.")
   time.sleep(1)
   if (count == 1):
     GPIO.cleanup()
   