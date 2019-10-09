#!flask/bin/python
from flask import Flask, jsonify, request
import RPi.GPIO as GPIO
import time as time

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

garage_door_relay_pin = 13
garage_unused_relay_pin = 16
garage_door_sensor_pin = 25
garage_lights_relay_pin = 19
#garage_red_button_pin = 26
#garage_white_button_pin = 21

GPIO.setup(garage_door_relay_pin,GPIO.OUT)
GPIO.setup(garage_door_sensor_pin,GPIO.OUT)
GPIO.setup(garage_lights_relay_pin,GPIO.OUT)
GPIO.setup(garage_unused_relay_pin,GPIO.OUT)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/door/', methods=['PUT', 'POST', 'GET'])
def door_task():
    if(request.method == 'GET'):
        state = GPIO.input(garage_door_relay_pin)
        if(state):
            return 'TRUE'
        else:
            return 'FALSE'
    else:
        relay_momentary_button(garage_door_relay_pin)
        time.sleep(20)
        state = sensor_read(garage_door_sensor_pin)
        if (state):
            return 'TRUE'
        else:
            return 'FALSE'

@app.route('/api/lights/', methods=['PUT', 'POST', 'GET'])
def light_task():
    if(request.method == 'GET'):
        state = GPIO.input(garage_lights_relay_pin)
        if (state):
            return 'TRUE'
        else:
            return 'FALSE'
    else:
        state = relay_state_change(garage_lights_relay_pin)
        if (state):
            return 'TRUE'
        else:
            return 'FALSE'

def sensor_read(pin):
    GPIO.output(pin, GPIO.High)
    state = GPIO.input(pin)
    GPIO.output(pin, GPIO.Low)
    return state

def relay_state_change(pin):
    state = GPIO.input(pin)
    GPIO.output(pin, not state)

def relay_momentary_button(pin):
    state = GPIO.input(pin)
    GPIO.output(pin,not state)
    time.sleep(.2)
    GPIO.output(pin, state)

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=8090)
