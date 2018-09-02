class Device:
    def __init__(self, device_dict):
        self.name = device_dict.get('device_name')
        self.id = device_dict.get('device_id')
        self.sensor_type = device_dict.get('sensor_type_name')
        self.sensor_id = device_dict.get('sensor_id')
        self.metric_names = device_dict.get('sensor_field_names')
        self.last_timestamp_written = None
