import json


class SdsStream(object):
    """SDS stream definition"""
    def __init__(self, stream_id, name, type_id, description):
        self.__id = stream_id
        self.__name = name
        self.__type_id = type_id
        self.__description = description

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
    def Description(self):
        return self.__description

    @Description.setter
    def Description(self, description):
        self.__description = description

    @property
    def TypeId(self):
        return self.__type_id

    @TypeId.setter
    def TypeId(self, typeId):
        self.__type_id = typeId

    def to_json(self):
        return json.dumps(self.to_dictionary())

    def to_dictionary(self):
        # required properties
        dictionary = {'Id': self.Id, 'TypeId': self.TypeId}

        # optional properties
        if hasattr(self, 'Name'):
            dictionary['Name'] = self.Name

        if hasattr(self, 'Description'):
            dictionary['Description'] = self.Description

        if hasattr(self, 'BehaviorId'):
            dictionary['BehaviorId'] = self.BehaviorId

        if hasattr(self, 'Indexes'):
            dictionary['Indexes'] = []
            for value in self.Indexes:
                dictionary['Indexes'].append(value.to_dictionary())

        return dictionary

    @staticmethod
    def from_json(json_obj):
        return SdsStream.from_dictionary(json_obj)

    @staticmethod
    def from_dictionary(content):
        stream = SdsStream()

        if len(content) == 0:
            return stream

        if 'Id' in content:
            stream.Id = content['Id']

        if 'Name' in content:
            stream.Name = content['Name']

        if 'Description' in content:
            stream.Description = content['Description']

        if 'TypeId' in content:
            stream.TypeId = content['TypeId']

        return stream
