import RPi.GPIO as GPIO
import time

class GPIOController:
    def __init__(self):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        self.pins = {
            'ac1': 4,
            'ac2': 17,
            'blower': 18,
            'e_fan': 27,
            'exhaust': 22
        }
        # GPIO.setwarnings(False)
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT)
        

    def turn_on(self, *devices):
        """Turn on multiple devices at once."""
        for device in devices:
            GPIO.output(self.pins[device], GPIO.LOW)

    def turn_off(self, *devices):
        """Turn off multiple devices at once."""
        for device in devices:
            GPIO.output(self.pins[device], GPIO.HIGH)

    def turn_on_timed(self, device, duration):
        """Turn on a device for a specific duration, then turn it off."""
        GPIO.output(self.pins[device], GPIO.LOW)
        time.sleep(duration)
        GPIO.output(self.pins[device], GPIO.HIGH)

    def turn_off_exhaust(self):
        self.turn_off('exhaust', 'exhaust')

    def turn_off_blower(self):
        self.turn_off('blower', 'blower')

    def turn_on_ac_units(self):
        self.turn_on('ac1', 'ac2')

    def turn_off_ac_units(self):
        self.turn_off('ac1', 'ac2')

    def turn_on_e_fans(self):
        self.turn_on('e_fan', 'e_fan')

    def turn_off_e_fans(self):
        self.turn_off('e_fan', 'e_fan')

    def turn_on_timed_blower(self):
        self.turn_on_timed('blower', 300)

    def turn_on_timed_exhaust(self):
        self.turn_on_timed('exhaust', 180)

    def cleanup(self):
        """Clean up all GPIO pins."""
        GPIO.cleanup()
