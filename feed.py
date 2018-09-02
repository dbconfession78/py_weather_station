from helper_functions import seconds_to_iso
"""
feed: contains class definition for 'Feed'
"""


class Feed:
    """Object form of La Crosse device metrics information"""
    def __init__(self, obj):
        """
        :param obj: raw response from La Crosse /feed API
        """
        self.field_names = list(obj.keys())
        self.metrics = {k: v.get('values') for k, v in obj.items()}
        self.most_recent_timestamp = None
        self.raw_feed = obj
        self.time_stamps = self.parse_timestamps()

    def parse_timestamps(self):
        """Sets 'self.most_recent_timestamp' and returns list of timestamps"""
        retval = []
        if self.metrics:
            first_key = list(self.metrics.keys())[0]
            for event in self.metrics.get(first_key):
                retval.append(event.get('u'))
        if retval:
            self.most_recent_timestamp = seconds_to_iso(retval[-1])
        return retval

    def construct_metric_dict(self, idx):
        """
        Puts all metrics sharing the same time key into a single dict object
        :param idx: the index (int) of the feed list desired for conversion
        """
        metric_dict = {}
        for field_name in self.field_names:
            metric_dict[field_name] = self.metrics[field_name][idx].get('s')
        return metric_dict
