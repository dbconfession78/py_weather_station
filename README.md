# Python Weather Station Sample

## Description
By connecting an actual device, this sample gives a more practical 
understanding on how to manage SDS types and streams.  Because SDS Client
Libraries are not available for Python developers, this sample illustrates
proper implementation using the SDS REST API.

For more detail on how to structure your SDS types and streams, please refer to
<a href="https://github.com/osisoft/Qi-Samples/blob/master/Extended/Python/PyPerfmonSample/readme.md">documentation</a>
for the <a href="https://github.com/osisoft/Qi-Samples/tree/master/Extended/Python/PyPerfmonSample">Python Performance Monitor</a>. 

## Requirements
1. <a href="https://www.amazon.com/Crosse-Technology-V40-Pro-Int-Wireless-Professional/dp/B07B5MKXPP/ref=sr_1_fkmr0_1?ie=UTF8&qid=1535742370&sr=8-1-fkmr0&keywords=La+Crosse+Technology+V40-Pro-Int+Color+Wireless++++Wi-Fi+Professional+Weather+Station+and+Console+Display">La Crosse Technology Wireless Multi-Sensor and Color Console Display</a>.
2. "La Crosse View" app* ( <a href="https://itunes.apple.com/us/app/la-crosse-view/id1006925791?mt=8">iOS</a>, <a href="https://play.google.com/store/apps/details?id=com.lacrosseview.app">Android</a> )
3. 2.4 GHz Wi-Fi connection (5.0 will not work)

\* follow setup instructions in the "La Crosse View" app before proceeding.

## Part 1 - Weather Station
#### 1. Connect your La Crosse View account
    def login(self, email, password):
        req_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyD-Uo0hkRIeDYJhyyIg-TvAv8HhExARIO4"
        payload = {
            "email": email,
             "returnSecureToken": True,
             "password": password
        }
        response = requests.post(req_url, data=json.dumps(payload))
        body = response.json()
        self.token = body.get('idToken')
<br>

#### 2. Get Account Locations
    def init_locations(self):
        req_url = "https://lax-gateway.appspot.com/_ah/api/lacrosseClient/v1.1/active-user/locations"
        headers = {"Authorization": "Bearer " + self.token}
        response = requests.get(req_url, headers=headers)
        body = response.json()
        for loc in body.get('items'):
            self.locations.append(Location(loc))
<br>

#### 3. Get Devices for each location
    def init_location_devices(self, location):
        req_ url = "https://lax-gateway.appspot.com/_ah/api/lacrosseClient/v1.1/active-user/location/"+ location.id\ + "/sensorAssociations?prettyPrint=false"
        headers = {"Authorization": "Bearer " + self.token}
        response = requests.get(req_url, headers=headers)
        body = response.json()
            
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
<br>

#### 4. Get feed from devices
    def request_feed(self, device, start=None, end=None):
        fields_list = device.metric_names
        fields_str = ",".join(fields_list)
        time_zone = "America/Los_Angeles"
        end = str(datetime_to_int_seconds(datetime.utcnow()))
        aggregates = "ai.ticks.1"
        start = "from={}&".format(start) if start else ""
        end = "to={}&".format(end) if end else ""
        req_url = "https://ingv2.lacrossetechnology.com/" \
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
            response = requests.get(req_url, headers=headers)
            body = response.json()
            return body.get('ref.user-device.' + device.id).get('ai.ticks.1').get('fields')
<br> 

## Part 2 - Sequential Data Store (SDS)
### 1. Setup SDS Type 
##### a. define type's structure
    def init_type(self, type_id, prop_names):
        sds_type = self.types.get(type_id)
        if not sds_type:
            type_id = type_id.lower().replace(' ', '_')
    
            sds_type = SdsType()
            sds_type.Id = type_id
            sds_type.name = type_id
            
            sds_type.sds_type_code = 1
            sds_type.Properties = []
    
            double_type = SdsType()
            double_type.Id = 'double_type'
            double_type.sds_type_code = 14
    
            date_time_type = SdsType()
            date_time_type.Id = "date_time_type"
            date_time_type.sds_type_code = 16
    
            time_prop = SdsTypeProperty()
            time_prop.Id = 'Time'
            time_prop.SdsType = date_time_type
            time_prop.IsKey = True
            sds_type.Properties.append(time_prop)
    
            for prop_name in prop_names:
                prop = SdsTypeProperty()
                prop.Id = prop_name
                prop.Name = prop_name
                prop.SdsType = double_type
                sds_type.Properties.append(prop)

##### b. retrieve type defined in (1a) if it exists otherwise add it
    def get_or_create_type(self, namespace_id, sds_type):
        req_url = "{}/api/Tenants/{}/Namespaces/{}/Types/{}"
            .format(self.url, self.tenantId, namespace_id, sds_type.Id)
        
        payload = sds_type.to_json()
        response = requests.post(
            url=req_url,
            data=payload,
            headers=self.__sds_headers())   
             
        sds_type = SdsType.from_json(json.loads(response.content))
        
        return sds_type
<br>

### 2. Setup SDS Stream
##### a. define stream
    sds_stream = SdsStream(stream_id=type_id, name=type_id, type_id=type_id)

##### b. update stream defined in (2a) if it exists otherwise add it 
    def create_or_update_stream(self, namespace_id, stream):
        req_url = "{}/api/Tenants/{}/Namespaces/{}/Streams/{}".format(
            self.url,
            self.tenantId,
            namespace_id,
            stream.Id)
    
        payload = stream.to_json()
        headers = self.__sds_headers()
        requests.put(url=req_url, data=payload, headers=headers)
<br>

### 3. Create an event with data to be written to SDS stream
    def next_event(type_id, event_dict, time_key=None):
        event = SdsTypeData(type_id=type_id, time=time_key)
        [event.__setattr__(list(event_dict.keys())[i], value) for i, value in enumerate(event_dict.values())]
        
        return event
<br>

### 4. Write event to SDS stream
     def update_value(self, namespace_id, stream_id, value):
        payload = value.to_json()
        req_url =  "{}/api/Tenants/{}/Namespaces/{}/Streams/{}/Data/UpdateValue".format(
            self.url,
            self.tenantId,
            namespace_id,
            stream_id)
            
        requests.put(url=req_url, data=payload headers=self.__sds_headers())
<br>

### 5. Validate event written in (4)*
    def get_last_value(self, namespace_id, stream_id, value_class, view_id=""):
        req_url = "{}/api/Tenants/{}/Namespaces/{}/Streams/{}/Data/GetLastValue".format(
                self.url,
                self.tenantId,
                namespace_id,
                stream_id)
        
        response = requests.get(req_url, headers=self.__sds_headers())    
        content = json.loads(response.content)
        
        return value_class.from_json(content)
\* Alternatively refer to `get_window_values` in `sds_client.py`
if you'd prefer to validate data after all events have been written
<br>
<br>

### 6. Delete a stream
    def delete_stream(self, namespace_id, stream_id):
        req_url = "{}/api/Tenants/{}/Namespaces/{}/Streams/{}".format(
            self.url,
            self.tenantId,
            namespace_id,
            stream_id)
             
        requests.delete(req_url, headers=self.__sds_headers())
<br>

### 7. Delete a type
\* A type cannot be deleted if any dependants remain (streams, views etc)

    def delete_type(self, namespace_id, type_id):
        req_url = "{}/api/Tenants/{}/ Namespaces/{}/Types/{}".format(
                    self.url,
                    self.tenantId,
                    namespace_id,
                    type_id) 
                    
        requests.delete(req_url, headers=self.__sds_headers())
