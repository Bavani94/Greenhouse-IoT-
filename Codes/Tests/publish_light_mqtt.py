from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import pyrebase
import spidev
import time
import json

spi= spidev.SpiDev()
spi.open(0,0)

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

# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
   adc = spi.xfer2([1,(8+channel)<<4,0])
   data = ((adc[1]&3) << 8) + adc[2]
   return data

def customCallback(client, userdata, message):
	print("Received new message: ")
	print(message.payload)
	print("From topic:")
	print(message.topic)
	print("----------------------")

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
rpi.subscribe("sensors/light", 1, customCallback)
sleep(2)

while True:
	light_value = ReadChannel(1)
	data = {'date': int(time.time()), 'light_value': str(light_value)}
	result = db.child("test_light_mqtt").push(data)
	json_string = json.dumps(data)
	rpi.publish("sensors/light", json_string, 1)
	sleep(2)