#!flask/bin/python
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import RPi.GPIO as GPIO
import time as time
import os

app = Flask(__name__)
api = Api(app)

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

class GarageDoor(Resource):
    def get(self):
        state = sensor_read(garage_door_sensor_pin)
        if(state):
            return {'state':'open'}
        else:
            return {'state':'closed'}

    def post(self):
        content = request.get_json()
        action = content['action']
        state = sensor_read(garage_door_sensor_pin)
        if (action == 'open'):
            if(state):
                relay_momentary_button(garage_door_relay_pin)
        elif (action == 'close'):
            state = sensor_read(garage_door_sensor_pin)
            if(not state):
                relay_momentary_button(garage_door_relay_pin)
        if(state):
            return {'state':'open'}
        else:
            return {'state':'closed'}


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
        if(state):
            return 'TRUE'
        else:
            return 'FALSE'

@app.route('/api/lights/', methods=['PUT', 'POST', 'GET'])
def light_task():
    if(request.method == 'GET'):
        state = GPIO.input(garage_lights_relay_pin)
        if(state):
            return 'TRUE'
        else:
            return 'FALSE'
    else:
        state = relay_state_change(garage_lights_relay_pin)
        if(state):
            return 'TRUE'
        else:
            return 'FALSE'

def sensor_read(pin):
    GPIO.output(pin, True)
    state = GPIO.input(pin)
    GPIO.output(pin, False)
    return state

def relay_state_change(pin):
    state = GPIO.input(pin)
    GPIO.output(pin, not state)
    return GPIO.input(pin)

def relay_momentary_button(pin):
    GPIO.output(pin, False)
    state = GPIO.input(pin)
    GPIO.output(pin,not state)
    time.sleep(.2)
    GPIO.output(pin, state)

api.add_resource(GarageDoor, '/api/GarageDoor')
app.run(host='0.0.0.0', port=8090, debug=True)
