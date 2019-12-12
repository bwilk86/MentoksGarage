import RPi.GPIO as GPIO
import time as time
import os
import markdown
import sys
from picamera import PiCamera

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

garage_door_relay_pin = 13
garage_unused_relay_pin = 16
garage_door_sensor_pin = 25
garage_lights_relay_pin = 19
# garage_red_button_pin = 26
# garage_white_button_pin = 21

GPIO.setup(garage_door_relay_pin, GPIO.OUT)
GPIO.setup(garage_door_sensor_pin, GPIO.OUT)
GPIO.setup(garage_lights_relay_pin, GPIO.OUT)
GPIO.setup(garage_unused_relay_pin, GPIO.OUT)


# TODO: refactor device types.
class RaspberryPiDevice:
    def perform_operation(self, device, operation):
        # get device_type

        if device['type'] == 'sensor':
            # Sensors should only have get operations, not puts
            return {
                'message': 'Sensors cannot perform operations, the proper use is GET',
                'device_id': device['id'],
                'device_name': device['name'],
                'requested_operation': operation,
                'success': False
            }
        elif device['type'] == 'toggle':
            # DO TOGGLE SWITCH WORK HERE
            return
        elif device['type'] == 'momentary':
            relay_momentary_button(device['output_pin'])
            return {
                'message': device['name'] + ' performed the requested action',
                'device_id': device['id'],
                'device_name': device['name'],
                'requested_operation': requested_operation,
                'success': True
            }

    # TODO: refactor for new object shape
    def get_sensor_state(self, sensor):
        # read from a sensor
        state = sensor_read(sensor['input_pin'], sensor['output_pin'])
        return state

    # TODO: refactor for new object shape
    def sensor_read(self, in_pin, out_pin):
        GPIO.output(out_pin, True)
        state = GPIO.input(in_pin)
        GPIO.output(out_pin, False)
        return state

    # TODO: refactor for new object shape
    def dep_sensor_read(self, pin):
        GPIO.output(pin, True)
        state = GPIO.input(pin)
        GPIO.output(pin, False)
        return state

    def relay_state_change(self, pin):
        state = GPIO.input(pin)
        GPIO.output(pin, not state)
        return GPIO.input(pin)

    def relay_momentary_button(self, pin):
        GPIO.output(pin, False)
        time.sleep(.2)
        GPIO.output(pin, True)
