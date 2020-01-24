""" Module to build an API """
import shelve
import os
import markdown

from flask import Flask, g
from flask_restful import Resource, Api, reqparse

# Create an instance of Flask
APP = Flask(__name__)

# Create the API
API = Api(APP)


def get_db():
    """ Mount Database """
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = shelve.open("devices.db")
    return database


@APP.teardown_appcontext
def teardown_db(exception):
    """ Destruct Database """
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()


@APP.route("/")
def index():
    """ Innitial page to show documentation. """

    # Open the README file
    with open(os.path.dirname(APP.root_path) + '/README.md', 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)

# pylint: disable=R0201


class DeviceList(Resource):
    """ Class to bring all devices and create new devices. """

    def get(self):
        """ Method to bring all devices. """
        shelf = get_db()
        keys = list(shelf.keys())

        devices = []

        for key in keys:
            devices.append(shelf[key])

        return {'message': 'Success', 'data': devices}

    def post(self):
        """ Method to create new devices. """
        parser = reqparse.RequestParser()

        parser.add_argument('identifier', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('device_type', required=True)
        parser.add_argument('controller_gateway', required=True)

        # Parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message': 'Device registered', 'data': args}, 201

# pylint: disable=R0201


class Device(Resource):
    """ Class to bring device and delete device """

    def get(self, identifier):
        """ Method to bring one device. """
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if identifier not in shelf:
            return {'message': 'Device not found', 'data': {}}, 404

        return {'message': 'Device found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        """ Method to delete one device. """
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if identifier not in shelf:
            return {'message': 'Device not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204


API.add_resource(DeviceList, '/devices')
API.add_resource(Device, '/device/<string:identifier>')
