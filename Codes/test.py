from gpiozero import LED

led = LED(4)
led.on()

while True:
	print('LALALA')