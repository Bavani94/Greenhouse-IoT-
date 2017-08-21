import pyrebase
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json

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

# Configure MQTT
host = "a2g49f96gkk39l.iot.ap-southeast-1.amazonaws.com"
rootCApath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

def lightCallBack(client, userdata, message):
  print("Received new message: ")
  print(message.payload)
  light_data = json.loads(message.payload)
  print(light_data)
  print("Sending to Firebase...")
  result = db.child("light_readings").push(light_data)
  print("Done sending to Firebase.")
  print("From topic:")
  print(message.topic)
  print("----------------------")

def waterCallBack(client, userdata, message):
  print("Received new message: ")
  print(message.payload)
  water_data = json.loads(message.payload)
  print(water_data)
  print("Sending to Firebase...")
  result = db.child("water_level").push(water_data)
  print("Done sending to Firebase.")
  print("From topic:")
  print(message.topic)
  print("----------------------")

def tempHumCallBack(client, userdata, message):
  print("Received new message: ")
  print(message.payload)
  temp_hum_data = json.loads(message.payload)
  print(temp_hum_data)
  print("Sending to Firebase...")
  result = db.child("temperature_humidity_readings").push(temp_hum_data)
  print("Done sending to Firebase.")
  print("From topic:")
  print(message.topic)
  print("----------------------")

def soilCallBack(client, userdata, message):
  print("Received new message: ")
  print(message.payload)
  soil_data = json.loads(message.payload)
  print(soil_data)
  print("Sending to Firebase...")
  result = db.child("soil_moisture_readings").push(soil_data)
  print("Done sending to Firebase.")
  print("From topic:")
  print(message.topic)
  print("----------------------")

rpi = AWSIoTMQTTClient("Firebase")
rpi.configureEndpoint(host, 8883)
rpi.configureCredentials(rootCApath, privateKeyPath, certificatePath)
rpi.configureOfflinePublishQueueing(-1)
rpi.configureDrainingFrequency(2)
rpi.configureConnectDisconnectTimeout(10)
rpi.configureMQTTOperationTimeout(5)
rpi.connect()
rpi.subscribe("sensors/light", 1, lightCallBack)
rpi.subscribe("sensors/waterlevel", 1, waterCallBack)
rpi.subscribe("sensors/temphum", 1, tempHumCallBack)
rpi.subscribe("sensors/soil", 1, soilCallBack)

while True:
  print("Waiting for MQTT message.")
  time.sleep(5)