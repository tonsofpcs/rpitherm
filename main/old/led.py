import RPi.GPIO as GPIO
# Use the pin numbers from the ribbon cable board.
GPIO.setmode(GPIO.BCM)
# Set up the pin you are using ("22" is an example) as output.
GPIO.setup(22, GPIO.OUT)
# Turn on the pin and see the LED light up.
GPIO.output(22, GPIO.HIGH)
# Turn off the pin to turn off the LED.
GPIO.output(22, GPIO.LOW)
