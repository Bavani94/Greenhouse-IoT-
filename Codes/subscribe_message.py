# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from gpiozero import MCP3008

from twilio.rest import Client

adc = MCP3008(channel=0)

water_level = None

# Custom MQTT message callback
def customCallback(client, userdata, message):
    global water_level
    print("Received a new message: ")
    print(message.payload)
    water_data = json.loads(message.payload)
    water_level = water_data["water_level"]
    print("from topic: ")
    print(message.topic)
    print("‐‐‐‐‐‐‐‐‐‐‐‐‐‐\n\n")

host = "a2g49f96gkk39l.iot.ap-southeast-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

account_sid = "AC8a1f779788050ebdb0b1613a906045bc"
auth_token = "1a8dcfe90663cbac11b7605d8c4c10e3"
client = Client(account_sid, auth_token)

## Twilio Settings - First is my phone number, second is the Twilio number.
my_hp = "+6596774923" #change the number if you want
twilio_hp = "+18603816312"

my_rpi = AWSIoTMQTTClient("basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(‐1)  
my_rpi.configureDrainingFrequency(2) 
my_rpi.configureConnectDisconnectTimeout(10) 
my_rpi.configureMQTTOperationTimeout(5) 

# Connect and subscribe to AWS IoT
my_rpi.connect()
except:
    print ("Unexpected error:", sys.exc_info() [0])
    
my_rpi.subscribe("sensors/waterlevel", 1, customCallback)
sleep(2)


# Publish in a loop
while True:
   if (water_level==0){
      sms = "Water level is now low. Please refill it as soon as possible"
      message = client.api.account.messages.create(to=my_hp,from_=twilio_hp,body=sms)
      sleep(60*10)
   }
