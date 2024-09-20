import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)


GPIO.output(19, GPIO.LOW)
GPIO.output(13, GPIO.LOW)

GPIO.cleanup()
