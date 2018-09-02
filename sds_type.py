from sds_type_property import SdsTypeProperty
import json


class SdsType(object):
    def __init__(self):
        # Please refer to the following link for an up-to-date listing of type
        # codes when assigning a type code to a new SdsType:
        # osisoft-edge.readthedocs.io/en/latest/Qi_Types.html#sdstypecode
        self.__type_code = 0
        self.__id = None
        self.__name = None
        self.__properties = []
        self.__description = None

    @property
    def Id(self):
        return self.__id

    @Id.setter
    def Id(self, id):
        self.__id = id

    @property
    def Name(self):
        return self.__name

    @Name.setter
    def Name(self, name):
        self.__name = name

    @property
    def Properties(self):
        return self.__properties

    @Properties.setter
    def Properties(self, properties):
        self.__properties = properties

    @property
    def Description(self):
        return self.__description

    @Description.setter
    def Description(self, description):
        self.__description = description

    @property
    def sds_type_code(self):
        return self.__type_code

    @sds_type_code.setter
    def sds_type_code(self, type_code):
        self.__type_code = type_code

    def to_json(self):
        return json.dumps(self.to_dictionary())

    def to_dictionary(self):
        dictionary = {'SdsTypeCode': self.sds_type_code}

        if hasattr(self, 'Properties'):
            dictionary['Properties'] = []
            for prop in self.Properties:
                dictionary['Properties'].append(prop.to_dictionary())

        if hasattr(self, 'Id'):
            dictionary['Id'] = self.Id

        if hasattr(self, 'Name'):
            dictionary['Name'] = self.Name

        if hasattr(self, 'Description'):
            dictionary['Description'] = self.Description

        return dictionary

    @staticmethod
    def from_json(json_obj):
        return SdsType.from_dictionary(json_obj)

    @staticmethod
    def from_dictionary(content):
        event_type = SdsType()

        if len(content) == 0:
            return event_type

        if 'Id' in content:
            event_type.Id = content['Id']

        if 'Name' in content:
            event_type.name = content['Name']

        if 'Description' in content:
            event_type.description = content['Description']

        if 'SdsTypeCode' in content:
            event_type.sds_type_code = content['SdsTypeCode']

        if 'BaseType' in content:
            event_type.BaseType = SdsType.from_dictionary(content['BaseType'])

        if 'Properties' in content:
            properties = content['Properties']
            if properties is not None and len(properties) > 0:
                event_type.Properties = []
                for prop in properties:
                    event_type.Properties.append(
                        SdsTypeProperty.from_dictionary(prop))

        return event_type
