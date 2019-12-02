import RPi.GPIO as GPIO
import time as time
import os
import markdown
import sys
import shelve

from flask import Flask, jsonify, request, g
from picamera import PiCamera
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
CORS(app)

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


def get_db(write_back):
    db = getattr(g, '_database', None)
    if db is None:
        db.g._database = shelve.open("devices.db", write_back)
    return db


@app.route('/')
@cross_origin()
def index():
    with open(os.path.dirname(app.root_path) + '/venv/ReadMe.txt', 'r') as markdown_file:
        content = markdown_file.read()
        return markdown.markdown(content)


# router for performing a device's operation
# pass the device ID and the operation you would like to perform
@api.resource('/api/operation/')
class Operation(Resource):
    def put(self):
        # parse the request and create argument list
        parser = reqparse.RequestParser()
        parser.add_argument('identifier', required=True)
        parser.add_argument('operation', required=True)
        args = parser.parse_args()

        # get the DB with no writeback (only reading the DB)
        shelf = get_db(False)

        # get the device from the DB to get it's operations/type
        try:
            device = shelf[args['identifier']]
        except KeyError:
            return {'message': 'Device not found for Key', 'error': KeyError}
        finally:
            shelf.close()

        device_type = device['type']
        available_operations = device['operations']
        requested_operation = args['operation']

        # Determine if this device does the requested operation, return if not.
        can_do_operation = False

        for op in available_operations:
            if op['operation'] == requested_operation:
                can_do_operation = True
                break

        if not can_do_operation:
            return {
                       'message': 'Device cannot perform the requested operation',
                       'device_id': device['identifier'],
                       'device_name': device['name'], 'operations': device['operations']
                   }, 400

        if device_type['controller'] == 'RPi':
            # DO RASPBERRY PI SPECIFIC STUFF
            if device_type['subType'] == 'sensor':
                # Sensors should only have get operations, not puts
                return {'message': 'Sensors cannot perform operations'}, 400
            elif device_type['subType'] == 'toggle':
                # DO TOGGLE SWITCH WORK HERE
                return 200
            elif device_type['subType'] == 'momentary':
                has_sensor = False
                if device['related_sensor_id'] is not None:
                    state = get_sensor_state(device['related_sensor_id'])
                    has_sensor = True

                if requested_operation == 'open':
                    if state is not None & state == 'open':
                        return {'message': device['name'] + ' is already open', 'state': state}, 200
                    else:
                        relay_momentary_button(device['output_pin'])
                        time.sleep(10)
                        if has_sensor:
                            state = get_sensor_state(device['related_sensor_id'])
                            return {'message': device['name'] + ' opened', 'state': state}, 200
                        else:
                            return {'message': device['name'] + ' opened'}, 200
                elif requested_operation == 'close':
                    if state is not None & state == 'close':
                        return {'message': device['name'] + ' is already closed', 'state': state}, 200
                    else:
                        relay_momentary_button(device['output_pin'])
                        time.sleep(10)
                        if has_sensor:
                            state = get_sensor_state(device['related_sensor_id'])
                            return {'message': device['name'] + ' closed', 'state': state}, 200
                        else:
                            return {'message': device['name'] + ' closed'}, 200
                return 200


@api.resource('/api/garagedoor/')
# @crossdomain(origin='*',headers=['access-control-allow-origin','Content-Type'])
class GarageDoor(Resource):
    def get(self):
        state = dep_sensor_read(garage_door_sensor_pin)
        if state:
            return {'message': 'Success', 'state': 'open'}, 200
        else:
            return {'message': 'Success', 'state': 'closed'}, 200

    def post(self):
        action = request.form.get('performprocess')
        state = dep_sensor_read(garage_door_sensor_pin)
        if action == 'open':
            if state:
                relay_momentary_button(garage_door_relay_pin)
        elif action == 'close':
            state = dep_sensor_read(garage_door_sensor_pin)
            if not state:
                relay_momentary_button(garage_door_relay_pin)
        if state:
            return {'message': 'Success', 'state': 'open'}, 200
        else:
            return {'message': 'Success', 'state': 'closed'}, 200


@app.route('/api/door/', methods=['PUT', 'POST', 'GET'])
@cross_origin()
def door_task():
    if request.method == 'GET':
        state = dep_sensor_read(garage_door_sensor_pin)
        if state:
            return {'message': 'Success', 'state': 'open'}, 200
        else:
            return {'message': 'Success', 'state': 'closed'}, 200
    else:
        action = request.form.get('performprocess')
        state = dep_sensor_read(garage_door_sensor_pin)
        if action == 'open':
            if state:
                relay_momentary_button(garage_door_relay_pin)
        elif action == 'close':
            state = dep_sensor_read(garage_door_sensor_pin)
            if not state:
                relay_momentary_button(garage_door_relay_pin)
        if state:
            return {'message': 'Success', 'state': 'open'}, 200
        else:
            return {'message': 'Success', 'state': 'closed'}, 200


@app.route('/api/garagecamera/', methods=['GET'])
@cross_origin()
def camera_task():
    camera = PiCamera()
    camera.start_preview()
    time.sleep(2)
    full_path = os.path.dirname(app.root_path) + '/camera/garage.jpg'
    camera.capture(full_path)
    camera.stop_preview()
    return {'message': 'Success', 'path': full_path}, 200


@app.route('/api/lights/', methods=['PUT', 'POST', 'GET'])
@cross_origin()
def light_task():
    if request.method == 'GET':
        state = GPIO.input(garage_lights_relay_pin)
        if state:
            return {'message': 'Success', 'state': 'ON'}, 200
        else:
            return {'message': 'Success', 'state': 'OFF'}, 200
    else:
        state = relay_state_change(garage_lights_relay_pin)
        if state:
            return {'message': 'Success', 'state': 'ON'}, 200
        else:
            return {'message': 'Success', 'state': 'OFF'}, 200


def get_sensor_state(sensor_id):
    # get the DB with no writeback (only reading the DB)
    shelf = get_db(False)

    # get the sensor from the DB to get it's type to determine how to interact
    try:
        sensor = shelf[sensor_id]
    except KeyError:
        return {'message': 'Sensor not found for ID: ' + sensor_id, 'error': KeyError}
    finally:
        shelf.close()
    # read from a sensor

    sensor_type = sensor['type']
    if sensor_type['controller'] == 'RPi':
        state = sensor_read(sensor['input_pin'], sensor['output_pin'])
        return state
    else:
        return None


def sensor_read(in_pin, out_pin):
    GPIO.output(out_pin, True)
    state = GPIO.input(in_pin)
    GPIO.output(out_pin, False)
    return state


def dep_sensor_read(pin):
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
    time.sleep(.2)
    GPIO.output(pin, True)


app.run(host='0.0.0.0', port=8090, debug=True)
