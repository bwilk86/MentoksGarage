import RPi.GPIO as GPIO
import time as time
import os
import markdown
import sys
import shelve
import RaspberryPiDevices

from flask import Flask, jsonify, request, g
from picamera import PiCamera
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
CORS(app)


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
            return {'message': 'Device not found for Key: ' + args['identifier'], 'error': KeyError}
        finally:
            shelf.close()

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

        # TODO: Implement Sensor logic
        if device['related_sensor_id'] is not None:
            related_sensor = get_sensor_from_db(device['related_sensor_id'])

            state_actual = get_sensor_state(related_sensor)
            if state_actual is not None:
                has_sensor = True
        else:
            has_sensor = False

        if has_sensor & state_actual is not None & state_actual == requested_operation:
            return {
                'message': device['name'] + ' is already in the requested state',
                'device_id': device['id'],
                'device_name': device['name'],
                'state': state_actual,
                'requested_operation': requested_operation,
                'success': True
            }, 200
        elif has_sensor & state_actual is None:
            return {
                'message': device['name'] + ' has a sensor(' + related_sensor['name'] + ', ' + related_sensor['id']
                + '), but it could not be read. The Sensor type has most likely not been implemented',
                'device_id': device['id'],
                'device_name': device['name'],
                'state': None,
                'requested_operation': requested_operation,
                'success': False
            }, 200

        if device['controller'] == 'RPi':
            response = RaspberryPiDevices.perform_operation(device, requested_operation)
            if has_sensor:
                state_actual = get_sensor_state(related_sensor)

                if response['success']:
                    return {
                        'message': response['message'],
                        'device_id': response['device_identifier'],
                        'device_name': response['device_name'],
                        'requested_operation': response['requested_operation'],
                        'state': state_actual
                        }, 200
                else:
                    return {
                        'message': response['message'],
                        'device_id': response['device_identifier'],
                        'device_name': response['device_name'],
                        'requested_operation': response['requested_operation'],
                        'state': state_actual
                        }, 500
            else:
                if response['success']:
                    return {
                        'message': response['message'],
                        'device_id': response['device_identifier'],
                        'device_name': response['device_name'],
                        'requested_operation': response['requested_operation']
                        }, 200
                else:
                    return {
                        'message': response['message'],
                        'device_id': response['device_identifier'],
                        'device_name': response['device_name'],
                        'requested_operation': response['requested_operation'],
                        }, 500
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


def get_sensor_from_db(sensor_id):
    # get the DB with no writeback (only reading the DB)
    shelf = get_db(False)
    # get the sensor from the DB to get it's type to determine how to interact
    try:
        sensor = shelf[sensor_id]
    except KeyError:
        return {'message': 'Sensor not found for ID: ' + sensor_id, 'error': KeyError}
    finally:
        shelf.close()
    return sensor


def get_sensor_state(sensor):
    sensor_type = sensor['type']
    if sensor_type['controller'] == 'RPi':
        return RaspberryPiDevices.get_sensor_state(related_sensor)
    else:
        return None



app.run(host='0.0.0.0', port=8090, debug=True)
