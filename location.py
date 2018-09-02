"""
location: contains the class defnition for 'Location'
"""


class Location:
    """Object form of La Crosse account location"""
    def __init__(self, loc_dict):
        """
        :param loc_dict: raw dict form of pertinent location info used to
        populate this object
        """
        if not loc_dict:
            raise Exception("Location initialization Error: "
                            "'loc_dict' is empty")
        self.id = loc_dict.get('id')
        self.name = loc_dict.get('name')
        self.devices = []
