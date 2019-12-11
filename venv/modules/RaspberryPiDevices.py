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


class RaspberryPiDevice:
    def perform_operation(self, device, operation):
        # get device_type
        device_type = device['type']

        if device_type['subType'] == 'sensor':
            # Sensors should only have get operations, not puts
            return {
                'message': 'Sensors cannot perform operations, the proper use is GET',
                'device_id': device['id'],
                'device_name': device['name'],
                'requested_operation': operation,
                'success': False
            }
        elif device_type['subType'] == 'toggle':
            # DO TOGGLE SWITCH WORK HERE
            return 200
        # TODO: remove all sensor logic, move to api layer (to do routing complexity where controller types don't match)
        elif device_type['subType'] == 'momentary':
            relay_momentary_button(device['output_pin'])
            time.sleep(10)
            return {
                'message': device['name'] + ' performed the requested action',
                'device_id': device['id'],
                'device_name': device['name'],
                'requested_operation': requested_operation,
                'state': state_actual,
                'success': True
            }

    def get_sensor_state(self, sensor):
        # read from a sensor
        state = sensor_read(sensor['input_pin'], sensor['output_pin'])
        return state

    def sensor_read(self, in_pin, out_pin):
        GPIO.output(out_pin, True)
        state = GPIO.input(in_pin)
        GPIO.output(out_pin, False)
        return state

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
