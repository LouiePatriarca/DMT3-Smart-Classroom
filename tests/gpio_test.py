import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)



GPIO.output(4, GPIO.LOW) #AC
GPIO.output(17, GPIO.LOW) #AC
GPIO.output(18, GPIO.HIGH) #BLOWER
GPIO.output(22, GPIO.HIGH) #EXHAUST
GPIO.output(27, GPIO.HIGH) #FAN

