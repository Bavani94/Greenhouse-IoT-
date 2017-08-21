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

# Configure GPIO
water_level_pin = 24

# Main loop - read raw data and display
while True:
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(water_level_pin, GPIO.IN)
   water_level = GPIO.input(water_level_pin)
   print (water_level)
   time.sleep(0.1)
   GPIO.cleanup()
   