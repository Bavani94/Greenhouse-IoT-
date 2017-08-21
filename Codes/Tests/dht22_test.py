import sys
import Adafruit_DHT
from time import sleep

pin = 26

while True:
 humidity, temperature = Adafruit_DHT.read_retry(11, pin)
 print('Temp: {:.1f} C'.format(temperature))
 print('Humidity: {:.1f}'.format(humidity))
 sleep(1)