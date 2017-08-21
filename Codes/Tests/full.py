#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# init list with pin numbers

pinList = [4, 17, 27, 22]

# loop through pins and set mode and state to 'high'

for i in pinList: 
    GPIO.setup(i, GPIO.OUT) 
    GPIO.output(i, GPIO.HIGH)

# time to sleep between operations in the main loop

SleepTimeL = 60
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
# main loop

try:
  GPIO.output(17, GPIO.LOW)
  GPIO.output(4, GPIO.LOW)
  print "Fan and Lights are ON"
  GPIO.output(20, GPIO.HIGH)
  print "Buzzer is ON"
  GPIO.output(21, GPIO.HIGH)
  print "Light is ON"
  time.sleep(SleepTimeL)
  GPIO.cleanup()
  print "Good bye!"

# End program cleanly with keyboard
except KeyboardInterrupt:
  print "  Quit"

  # Reset GPIO settings
  GPIO.cleanup()


# find more information on this script at
# http://youtu.be/WpM1aq4B8-A