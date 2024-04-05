'''
Created on April 3, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''
from intelligence.intelligence import Intelligence
import signals.dashboard as dashboard
import utilities.utilities as utilities

from devices.camera.camera_ip import CameraDevice

# Time window to keep in the transition matrix
TRANSITION_MATRIX_TIME_WINDOW_MS = utilities.ONE_MINUTE_MS * 15

# Time window to monitor for recent event tags
RECENT_EVENT_TAGS_TIME_WINDOW_MS = utilities.ONE_MINUTE_MS * 5

class LocationIPCameraEventsMicroservice(Intelligence):
    """
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        # Microservices extend the Intelligence class, which can be found in com.ppc.Bot/intelligence/intelligence.py
        # Always initialize your parent Intelligence class at the beginning!
        # This will generate a unique ID for your microservice, and assign your 'self.parent' object.
        # Device microservice's parent object is an actual Device object which will be an extension of the Device class found in com.ppc.Bot/devices/device.py.
        # Location microservice's parent object is the Location object found in com.ppc.Bot/locations/location.py.
        Intelligence.__init__(self, botengine, parent)
        
        # Transition matrix
        # Describes when a tag moves from one camera to another
        # [ (camera1, camera2, {tag: [(timestamp1, timestamp2)]}), ...]
        self.transition_matrix = []

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">initialize()")
        return
    
    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">new_version()")
        if not hasattr(self, 'transition_matrix'):
            self.transition_matrix = []
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">destroy()")
        return

    def get_html_summary(self, botengine, oldest_timestamp_ms, newest_timestamp_ms, test_mode=False):
        """
        Return a human-friendly HTML summary of insights or status of this intelligence module to report in weekly and test mode emails
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds to summarize
        :param newest_timestamp_ms: Newest timestamp in milliseconds to summarize
        :param test_mode: True to add or modify details for test mode, instead of a general weekly summary
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_html_summary()")
        return ""

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">mode_updated()")

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">device_measurements_updated()")
        # Check if the device object is a CameraDevice
        if isinstance(device_object, CameraDevice):
            # Log all camera event tags
            event_tags_by_camera = [(device_object, device_object.get_recent_event_tags()) for device_object in self.parent.devices.values() if isinstance(device_object, CameraDevice)]
            sorted_event_tags = sorted(event_tags_by_camera, key=lambda x: x[1])
            import json
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(f"Event Tags: {json.dumps(['{} {}: {}'.format(self.parent.get_local_datetime_from_timestamp(botengine, event_tags[1][1]), event_tags[0].description, event_tags[1][0]) for event_tags in sorted_event_tags], indent=2)}")
            
            # Build the transition matrix
            for camera1, event_tags1 in sorted_event_tags:
                for camera2, event_tags2 in sorted_event_tags:
                    if camera1 != camera2:
                        # Check if the transition matrix already has this camera transition
                        matrix = None
                        for _matrix in self.transition_matrix:
                            if (camera1 == _matrix[1] and camera2 == _matrix[0]):
                                matrix = _matrix
                                break
                        if matrix is None:
                            matrix = (camera2, camera1, {})
                            self.transition_matrix.append(matrix)

                        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(f"Matrix: {matrix}")
                        # Check if the event tags are the same
                        for tag in event_tags1[0]:
                            if tag in event_tags2[0]:
                                if event_tags1[1] > event_tags2[1]:
                                    botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(f"Tag Match: {tag}")

                                    # Check if the tag is already in the matrix
                                    matrix_tag = []
                                    if tag in matrix[2]:
                                        matrix_tag = matrix[2][tag]

                                    # Check if this timestamp is already in the matrix tag
                                    timestamp = (event_tags1[1], event_tags2[1])
                                    if timestamp not in matrix_tag:
                                        matrix_tag.append(timestamp)
                                        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(f"Matrix Tag: {matrix_tag}")
                                        # Prune the matrix to online include the last 15 minutes
                                        original_count = len(matrix_tag)
                                        matrix_tag = [t for t in matrix_tag if t[1] > botengine.get_timestamp() - TRANSITION_MATRIX_TIME_WINDOW_MS]
                                        if len(matrix_tag) != original_count:
                                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(f"Pruned Matrix Tag: {original_count} >> {len(matrix_tag)}")
                                    
                                    matrix[2][tag] = matrix_tag

            # Log the transition matrix
            """
            [
            "Camera-1 >> Camera-2: {'Person': [], 'Talking': [(1712172756797, 1712172466935)]}",
            "Camera-1 >> Camera-3: {'Person': [], 'Talking': [(1712183580223, 1712183424848)]}",
            "Camera-1 >> Camera-4: {'Person': [], 'Talking': [(1712184293590, 1712183857798)]}",
            "Camera-2 >> Camera-1: {'Person': [(1712175363193, 1712175094039)], 'Talking': []}",
            "Camera-2 >> Camera-3: {'Person': [(1712185575248, 1712185325053), (1712185806800, 1712185325053), (1712185999600, 1712185872776)], 'Talking': [(1712184541373, 1712184479949)]}",
            "Camera-2 >> Camera-4: {'Person': [(1712185785389, 1712185325053)], 'Talking': []}",
            "Camera-3 >> Camera-1: {'Person': [(1712184404147, 1712184189775)], 'Talking': [(1712183167251, 1712183079547), (1712183424848, 1712183410198), (1712183857798, 1712183580223)]}",
            "Camera-3 >> Camera-2: {'Person': [(1712185849935, 1712185806800), (1712185872776, 1712185806800)], 'Talking': [(1712174666641, 1712174641936)]}",
            "Camera-3 >> Camera-4: {'Person': [(1712184373888, 1712184189775)], 'Talking': [(1712185750689, 1712185741799), (1712185999489, 1712185971098)]}",
            "Camera-4 >> Camera-1: {'Person': [(1712184404147, 1712184373888)], 'Talking': [(1712183424848, 1712183233435), (1712183857798, 1712183233435)]}",
            "Camera-4 >> Camera-2: {'Person': [(1712185849935, 1712185785389), (1712185872776, 1712185785389)], 'Talking': [(1712174360698, 1712174240526)]}",
            "Camera-4 >> Camera-3: {'Person': [(1712185806800, 1712185785389)], 'Talking': [(1712186040047, 1712185999489), (1712186172248, 1712185999489)]}"
            ]

            [
            "Camera-1 >> Camera-2: {'Person': 0, 'Talking': 1}",
            "Camera-1 >> Camera-3: {'Person': 0, 'Talking': 1}",
            "Camera-1 >> Camera-4: {'Person': 0, 'Talking': 1}",
            "Camera-2 >> Camera-1: {'Person': 1, 'Talking': 0}",
            "Camera-2 >> Camera-3: {'Person': 3, 'Talking': 1}",
            "Camera-2 >> Camera-4: {'Person': 1, 'Talking': 0}",
            "Camera-3 >> Camera-1: {'Person': 1, 'Talking': 3}",
            "Camera-3 >> Camera-2: {'Person': 2, 'Talking': 1}",
            "Camera-3 >> Camera-4: {'Person': 1, 'Talking': 2}",
            "Camera-4 >> Camera-1: {'Person': 1, 'Talking': 2}",
            "Camera-4 >> Camera-2: {'Person': 2, 'Talking': 1}",
            "Camera-4 >> Camera-3: {'Person': 1, 'Talking': 2}"
            ]

            """
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(f"Transition Matrix: {json.dumps(['{} >> {}: {}'.format(camera1.description, camera2.description, '{}'.format(tags)) for camera1, camera2, tags in sorted(sorted(self.transition_matrix , key=lambda x: x[1].description), key=lambda x: x[0].description)], indent=2)}")
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(f"Transition Matrix: {json.dumps(['{} >> {}: {}'.format(camera1.description, camera2.description, '{}'.format({tag: len(tags[tag]) for tag in tags.keys()})) for camera1, camera2, tags in sorted(sorted(self.transition_matrix , key=lambda x: x[1].description), key=lambda x: x[0].description)], indent=2)}")

            # Check for significant tags (i.e., "Glass Breaking")
            if device_object.get_recent_event_tags() is not None:
                for tag in device_object.get_recent_event_tags()[0]:
                    if tag == "Glass Breaking":
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(f"Glass Breaking Event Detected!")
                        # Check recent tags for this camera
                        comment = _("A glass breaking event was detected on the camera.")
                        for event_tags in device_object.get_all_event_tags():
                            if not event_tags[1] > botengine.get_timestamp() - RECENT_EVENT_TAGS_TIME_WINDOW_MS:
                                # Skip this event tag if it's older than 5 minutes
                                continue
                            # If there is a "Vehicle" in our recent tags, then we have a possible vehicle event
                            if "Vehicle" in event_tags[0]:
                                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(f"Vehicle Event Detected!")
                                comment = _("Glass breaking was detected recently after a vehicle was detected on the camera. Please review the footage.")
                                break

                        dashboard.update_dashboard_header(botengine,
                                          self.parent,
                                          "glass_breaking",
                                          priority=dashboard.DASHBOARD_PRIORITY_CRITICAL_ALERT,
                                          percent_good=100,
                                          title=_("Glass Breaking Event Detected!"),
                                          comment=comment,
                                          icon="explosion",
                                          icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                                          resolution_object=dashboard.oneshot_resolution_object(botengine,
                                                                                                "glass_breaking",
                                                                                                dashboard_button=_("DISMISS >"),
                                                                                                actionsheet_title=_("Update Status"),
                                                                                                resolution_button=_("Dismiss"),
                                                                                                ack=_("Okay, dismissing the notification..."),
                                                                                                icon="thumbs-up",
                                                                                                icon_font="far",
                                                                                                response_options=None),
                                          conversation_object=None,
                                          future_timestamp_ms=None,
                                          ttl_ms=utilities.ONE_MINUTE_MS * 30)
                        break
            pass

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<device_measurements_updated()")
        return

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">device_metadata_updated()")
        return

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert.
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">device_alert()")
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">device_deleted()")
        return

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">question_answered()")
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">datastream_updated()")
            getattr(self, address)(botengine, content)
        return

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">schedule_fired()")
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">timer_fired()")
        return

    def file_uploaded(self, botengine, device_object, file_id, filesize_bytes, content_type, file_extension):
        """
        A device file has been uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file_id: File ID to reference this file at the server
        :param filesize_bytes: The file size in bytes
        :param content_type: The content type, for example 'video/mp4'
        :param file_extension: The file extension, for example 'mp4'
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">file_uploaded()")
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">coordinates_updated()")
        return