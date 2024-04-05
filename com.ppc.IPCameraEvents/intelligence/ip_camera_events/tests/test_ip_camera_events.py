
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities

from devices.camera.camera_ip import CameraDevice

from intelligence.ip_camera_events.device_ip_camera_microservice import *
from intelligence.ip_camera_events.location_ip_camera_events_microservice import *

import binascii
import json

import unittest
from unittest.mock import patch, MagicMock

class TestIPCameraEvents(unittest.TestCase):

    def test_ip_camera_events_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_object = CameraDevice(botengine, location_object, "_device_id_", 7004, "IP Camera")
        
        location_object.devices = {device_object.device_id: device_object}

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = LocationIPCameraEventsMicroservice(botengine, location_object)
        assert mut is not None

        mut = location_object.intelligence_modules["intelligence.ip_camera_events.location_ip_camera_events_microservice"]
        assert mut is not None

        mut = DeviceIPCameraMicroservice(botengine, location_object)
        assert mut is not None

        mut = device_object.intelligence_modules["intelligence.ip_camera_events.device_ip_camera_microservice"]
        assert mut is not None