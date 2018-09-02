import datetime
import json


class SdsTypeData:
    def __init__(self, type_id, prop_names=None, time=None):
        self.type_id = type_id
        self.time = time
        self.prop_names = prop_names

    def to_json(self):
        return json.dumps(self.to_dictionary())

    def to_dictionary(self):
        if self.time:
            time = self.time
        else:
            time = datetime.datetime.utcnow()
        dictionary = {'Time': str(time), 'Typeid': self.type_id}
        for k, v in self.__dict__.items():
            if k != "time" and k != "type_id" and k != "prop_names":
                dictionary[k] = v
        return dictionary

    def from_json(self, json_obj):
        return self.from_dictionary(json_obj)

    def from_dictionary(self, content):
        if self is None:
            return SdsTypeData()
        data_obj = SdsTypeData(type_id=self.type_id)
        data_obj.__setattr__('time', content['Time'])
        for prop in self.prop_names:
            # Pre-Assign the default
            if prop != 'time':
                data_obj.__setattr__(prop, 0)
                if prop in content:
                    value = content[prop]
                    if value is not None:
                        data_obj.__setattr__(prop, value)
        return data_obj
