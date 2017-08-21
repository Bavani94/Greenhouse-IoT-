#!/usr/bin/python

# Monitor two soil sensors on MCP3008, ch 2 and 3 
# (pin 3 and 4)

import spidev
import time
import os

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
   adc = spi.xfer2([1,(8+channel)<<4,0])
   data = ((adc[1]&3) << 8) + adc[2]
   return data

# Main loop - read raw data and display
while True:
   moisture_value = ReadChannel(0)
   dryness_percentage = moisture_value / 10.24
   print ("Moisture Value: " + str(moisture_value) + " Dryness Percentage: " + str(round(dryness_percentage, 2)))
   