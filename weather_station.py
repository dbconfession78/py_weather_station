from device import Device
from location import Location
import requests
import json
from datetime import datetime
from helper_functions import datetime_to_int_seconds


class WeatherStation:
    def __init__(self, config):
        self.config = config
        self.token = None
        self.locations = []
        self.__type_names = []
        self.__devices_by_location = {}
        self.__devices = []
        self.init_weather_station()
        self.has_new_data = False

    @property
    def type_names(self):
        return self.__type_names

    @type_names.setter
    def type_names(self, type_names):
        self.__type_names = type_names

    @property
    def devices_by_location(self):
        return self.__devices_by_location

    @devices_by_location.setter
    def devices_by_location(self, devices_by_location):
        self.__devices_by_location = devices_by_location

    @property
    def devices(self):
        return self.__devices

    @devices.setter
    def devices(self, devices):
        self.__devices = devices

    def login(self, email, password):
        print("Logging in...")
        url = "https://www.googleapis.com/" \
              "identitytoolkit/v3/relyingparty/verifyPassword?" \
              "key=AIzaSyD-Uo0hkRIeDYJhyyIg-TvAv8HhExARIO4"
        payload = {
            "email": email,
            "returnSecureToken": True,
            "password": password
        }
        r = requests.post(url, data=json.dumps(payload))
        body = r.json()
        self.token = body.get('idToken')

        if self.token is None:
            raise Exception("Login Failed. Check credentials and try again")

    def init_locations(self):
        url = "https://lax-gateway.appspot.com/" \
              "_ah/api/lacrosseClient/v1.1/active-user/locations"
        headers = {"Authorization": "Bearer " + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code < 200 or r.status_code >= 300:
            raise ConnectionError("failed to get locations ()".
                                  format(r.status_code))
        body = r.json()
        for loc in body.get('items'):
            self.locations.append(Location(loc))
        if not self.locations:
            raise Exception("Unable to get account locations")
        return True

    def init_weather_station(self):
        self.login(self.config.get("Credentials", "email"),
                   self.config.get("Credentials", "password"))
        if self.token:
            self.init_locations()
            print('Locations:')
            [print("\t- {} ({})".format(
                loc.name, loc.id)) for loc in self.locations]

        if self.locations:
            for loc in self.locations:
                self.init_location_devices(loc)
                print("Devices for location, '{}':".format(loc.name))
                devices = loc.devices
                [print("\t - {} ({})".format(d.name, d.id)) for d in devices]
                print()

            if all([loc.devices == [] for loc in self.locations]):
                raise Exception("init_weather_station(): there are no "
                                "devices in any of the locations")

    def init_type_names(self):
        if self.locations:
            for loc in self.locations:
                self.type_names += [d.name for d in loc.devices]
            if not self.type_names:
                raise Exception("get_type_names(): Failed to retrive type "
                                "names")

    def init_location_devices(self, location):
        url = "https://lax-gateway.appspot.com/" \
              "_ah/api/lacrosseClient/v1.1/active-user/location/"\
              + location.id\
              + "/sensorAssociations?prettyPrint=false"
        headers = {"Authorization": "Bearer " + self.token}
        r = requests.get(url, headers=headers)
        body = r.json()
        if body:
            devices = body.get('items')
            for device in devices:
                sensor = device.get('sensor')
                device_name = device.get('name').lower().replace(' ', '_')
                device_dict = {
                    "device_name": device_name,
                    "device_id": device.get('id'),
                    "sensor_type_name": sensor.get('type').get('name'),
                    "sensor_id": sensor.get('id'),
                    "sensor_field_names": [x for x in sensor.get('fields')
                                           if x != "NotSupported"],
                    "last_timestamp_written": None,
                    "location": location}
                device_obj = Device(device_dict)
                location.devices.append(device_obj)
                self.devices.append(device_obj)
            print()
        if not location.devices:
            print("get_location_devices() ERROR:  There are no devices for "
                  "location, {}".format(location.get('name')))

    def request_feed(self, device, start=None, end=None):
        if not device or not device.metric_names:
            return {}
        fields_list = device.metric_names
        if fields_list:
            fields_str = ",".join(fields_list)
        else:
            fields_str = fields_list

        time_zone = "America/Los_Angeles"
        end = str(datetime_to_int_seconds(datetime.utcnow())) \
            if end == 'now' else end
        aggregates = "ai.ticks.1"

        start = "from={}&".format(start) if start else ""
        end = "to={}&".format(end) if end else ""

        url = "https://ingv2.lacrossetechnology.com/" \
              "api/v1.1/active-user/device-association/ref.user-device.{id}/" \
              "feed?fields={fields}&" \
              "tz={tz}&" \
              "{_from}" \
              "{to}" \
              "aggregates={agg}&" \
              "types=spot".format(id=device.id,
                                  fields=fields_str, tz=time_zone,
                                  _from=start, to=end, agg=aggregates)

        headers = {"Authorization": "Bearer " + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code < 200 or r.status_code >= 300:
            print("{}: Failed to get feed".format(datetime.utcnow()))
            return False

        body = r.json()
        return body.get(
            'ref.user-device.' + device.id).get('ai.ticks.1').get('fields')
