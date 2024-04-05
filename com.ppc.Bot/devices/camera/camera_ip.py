'''
Created on April 3, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

from devices.device import Device


class CameraDevice(Device):
    """Camera Device"""

    # Measurement Names
    MEASUREMENT_NAME_EVENT_TAGS = 'eventTags'
    MEASUREMENT_NAME_EVENT_TYPE = 'eventType'

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [7004]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)
    
    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        Device.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("IP Camera")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "camera-ip"
    
    def get_recent_event_tags(self):
        """
        Get the event tags
        :return: (List of event tags, timestamp)
        """
        if CameraDevice.MEASUREMENT_NAME_EVENT_TAGS in self.measurements:
            return self.measurements[CameraDevice.MEASUREMENT_NAME_EVENT_TAGS][0]
        return None
    
    def get_all_event_tags(self):
        """
        Get the event tags
        :return: (List of event tags, timestamp)
        """
        if CameraDevice.MEASUREMENT_NAME_EVENT_TAGS in self.measurements:
            return self.measurements[CameraDevice.MEASUREMENT_NAME_EVENT_TAGS]
        return None
    
    #===========================================================================
    # CSV methods for machine learning algorithm integrations
    #===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a standardized .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        return Device.get_csv(self, botengine, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms, params=[CameraDevice.MEASUREMENT_NAME_EVENT_TAGS, CameraDevice.MEASUREMENT_NAME_EVENT_TYPE])