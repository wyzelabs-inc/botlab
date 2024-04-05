MICROSERVICES = {
    "DEVICE_MICROSERVICES": {
        7004: [
            {
                "module": "intelligence.ip_camera_events.device_ip_camera_microservice", 
                "class": "DeviceIPCameraMicroservice"
            }
        ],
    },
    "LOCATION_MICROSERVICES": [
        {
            "module": "intelligence.ip_camera_events.location_ip_camera_events_microservice", 
            "class": "LocationIPCameraEventsMicroservice"
        }
    ]
}
