import RPi.GPIO as GPIO
import time as time
import os
import markdown
from flask import Flask, jsonify, request, g
from picamera import PiCamera
import sys
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

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
@cross_origin()
def index():
    with open(os.path.dirname(app.root_path) + '/venv/ReadMe.txt', 'r') as markdown_file:
        content = markdown_file.read()
        return markdown.markdown(content)

@api.resource('/api/garagedoor/')
class GarageDoor(Resource):
    def get(self):
        state = sensor_read(garage_door_sensor_pin)
        if (state):
            data = {'state': 'open'}
            return jsonify(data)
        else:
            data = {'state': 'closed'}
            return jsonify(data)

    def post(self):
        action = request.form.get('performprocess')
        state = sensor_read(garage_door_sensor_pin)
        if (action == 'open'):
            if (state):
                relay_momentary_button(garage_door_relay_pin)
        elif (action == 'close'):
            state = sensor_read(garage_door_sensor_pin)
            if (not state):
                relay_momentary_button(garage_door_relay_pin)
        if (state):
            data = {'state': 'open'}
            return jsonify(data)
        else:
            data = {'state': 'closed'}
            return jsonify(data)

@app.route('/api/door/', methods=['PUT', 'POST', 'GET'])
@cross_origin()
def door_task():
    if(request.method == 'GET'):
        state = sensor_read(garage_door_sensor_pin)
        if (state):
            data = {'state':'open'}
            return jsonify(data), 200
        else:
            data={'state':'closed'}
            return jsonify(data), 200
    else:
        action = request.form.get('performprocess')
        state = sensor_read(garage_door_sensor_pin)
        if (action == 'open'):
            if (state):
                relay_momentary_button(garage_door_relay_pin)
        elif (action == 'close'):
            state = sensor_read(garage_door_sensor_pin)
            if (not state):
                relay_momentary_button(garage_door_relay_pin)
        if (state):
            data = {'state': 'open'}
            return jsonify(data), 200
        else:
            data = {'state': 'closed'}
            return jsonify(data), 200

@app.route('/api/garagecamera/', methods=['GET'])
@cross_origin()
def camera_task():
    camera = PiCamera()
    camera.start_preview()
    time.sleep(2)
    full_path = os.path.dirname(app.root_path) + '/camera/garage.jpg'
    camera.capture(full_path)
    camera.stop_preview()
    data = {'path': full_path}
    return jsonify(data)

@app.route('/api/lights/', methods=['PUT', 'POST', 'GET'])
@cross_origin()
def light_task():
    if(request.method == 'GET'):
        state = GPIO.input(garage_lights_relay_pin)
        if(state):
            data = {'state':'ON'}
            return jsonify(data), 200
        else:
            data = {'state': 'OFF'}
            return jsonify(data), 200
    else:
        state = relay_state_change(garage_lights_relay_pin)
        if(state):
            data = {'state': 'ON'}
            return jsonify(data), 200
        else:
            data = {'state': 'OFF'}
            return jsonify(data), 200

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
    state = GPIO.input(pin)
    GPIO.output(pin,False)
    time.sleep(.2)
    GPIO.output(pin, True)

app.run(host='0.0.0.0', port=8090, debug=True)
