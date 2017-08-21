from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time
import pyrebase
import picamera

c = picamera.PiCamera()
bools = False

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

# Cloudinary Configuration
cloudinary.config(
  cloud_name = "overkill",
  api_key = "876111269332755",
  api_secret = "8AMs3sZqg5HgEJiRFr9HuEUwzoA"
)
camera = 888
lightValue = None
lightStatus = None
fanValue = None
fanStatus = None

pumpValue = None
pumpStatus = None

cameraValue = None
# Configure GPIO
led_pin = 18
water_pump_pin = 20
fan_pin = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(water_pump_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)

# LED
GPIO.output(led_pin, GPIO.LOW)

# Water Pump
GPIO.output(water_pump_pin, GPIO.HIGH)

# Fan
GPIO.output(fan_pin, GPIO.LOW)

#Configure MQTT
host = "a2g49f96gkk39l.iot.ap-southeast-1.amazonaws.com"
rootCApath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

def lightControlCallback(client, userdata, message):
  global lightValue
  global lightStatus
  print("Received new message: ")
  print(message.payload)
  json_data = json.loads(message.payload)
  lightValue = int(json_data["value"])
  lightStatus = json_data["status"]
  print("From topic:")
  print(message.topic)
  print("----------------------")

def pumpControlCallback(client, userdata, message):
  global pumpValue
  global pumpStatus
  global pumpDuration
  print("Received new message: ")
  print(message.payload)
  json_data = json.loads(message.payload)
  pumpValue = int(json_data["value"])
  pumpStatus = json_data["status"]
  pumpDuration = json_data["duration"]
  print("From topic:")
  print(message.topic)
  print("----------------------")

def fanControlCallback(client, userdata, message):
  global fanValue
  global fanStatus
  print("Received new message: ")
  print(message.payload)
  json_data = json.loads(message.payload)
  fanValue = int(json_data["value"])
  fanStatus = json_data["status"]
  print("From topic:")
  print(message.topic)
  print("----------------------")

def cameraControlCallback(client, userdata, message):
  global cameraValue
  global bools
  print("Received new message: ")
  print(message.payload)
  json_data = json.loads(message.payload)
  cameraValue = int(json_data["value"])
  print("From topic:")
  print(message.topic)
  print("----------------------")
  bools = False


rpi = AWSIoTMQTTClient("control")
rpi.configureEndpoint(host, 8883)
rpi.configureCredentials(rootCApath, privateKeyPath, certificatePath)
rpi.configureOfflinePublishQueueing(-1)
rpi.configureDrainingFrequency(2)
rpi.configureConnectDisconnectTimeout(10)
rpi.configureMQTTOperationTimeout(5)
rpi.connect()
rpi.subscribe("sensors/commands/light", 1, lightControlCallback)
rpi.subscribe("sensors/commands/pump", 1, pumpControlCallback)
rpi.subscribe("sensors/commands/fan", 1, fanControlCallback)
rpi.subscribe("sensors/commands/camera", 1, cameraControlCallback)

while True:
  pumpDuration = db.child("pump_status").child("duration").get().val()
  print("Waiting for command.")
  # Logic for LED
  if lightValue == led_pin:
    if lightStatus == 'On':
      GPIO.output(led_pin, GPIO.HIGH)
      print("LED turned on.")
    else:
      GPIO.output(led_pin, GPIO.LOW)
      print("LED turned off.")
    # Logic for Water Pump
  if pumpValue == water_pump_pin:
    if pumpStatus == 'On':
      GPIO.output(water_pump_pin, GPIO.LOW)
      time.sleep(pumpDuration)
      print("Water pump turned on.")
    else:
      GPIO.output(water_pump_pin, GPIO.HIGH)
      print("Water pump turned off.")
  # Logic for Fan
  if fanValue == fan_pin:
    if fanStatus == 'On':
      GPIO.output(fan_pin, GPIO.HIGH)
      print("Fan turned on.")
    else:
      GPIO.output(fan_pin, GPIO.LOW)
      print("Fan turned off.")
    # Logic for Camera
  if cameraValue == camera and bools == False:
    global bools
    bools = True
    timestamp = int(time.time())
    filename = '/home/pi/photo_'+str(timestamp)+'.jpg'
    c.capture(filename)
    upload_response = cloudinary.uploader.upload_large(filename, resource_type = "auto")
    url = str(upload_response['secure_url'])
    data = { 'image_url' : url, 'date': timestamp }
    result = db.child("captured_images").push(data)
  time.sleep(5)