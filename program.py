from sdspy import *
"""
program: contains the main class 'Program'
"""


class Program:
    """Defines the main wrapper class"""
    def __init__(self, config):
        """
        config: parameters from local config.ini
        ws: contains attributes related to La Crosse View weather station
        sds: contains attributes related to Sequential Data Store (SDS)
        """
        self.config = config
        self.ws = WeatherStation(self.config)
        self.sds = SequentialDataStore(self.config, self.ws)
        self.start = None

    def run(self):
        """Executes the program"""
        for location in self.ws.locations:
            self.gather_data_over_time(
                location,
                freq=float(self.config.get("Preferences", "Frequency")),
                dur=float(self.config.get("Preferences", "Duration")))

        if self.print_session_events(self.start):
            print("Cleaning up...")
            cleanup(self.sds.client,
                    self.sds.namespace_id,
                    type_ids=[device.name for device in self.ws.devices])
        else:
            print("No streams or types were created this session")

    def print_session_events(self, start):
        """Reads from SDS and outputs all events written during current
        session"""
        print("Reading from SDS...")

        events_written_this_session = self.sds.from_sds(start)
        if not events_written_this_session:
            print("No events were written this session")
            return False

        for device in events_written_this_session:
            device_name = device[0].type_id
            print("'{}'".format(device_name))
            print("=" * len(device_name) + "==")
            for event in device:
                print(to_string(event))
            print()
        return True

    def gather_data_over_time(self, location, freq, dur):
        """Checks for new data from devices at location param and based on
        frequency and duration parameters"""
        if freq > dur:
            raise Exception("Frequency can't be higher than duration")
        i = dur
        while i > 0:
            print("Time remaining: {} seconds".format(i))
            for dev in location.devices:
                f = Feed(self.ws.request_feed(dev))
                if not f.metrics:
                    print("There is no collected data for '{}'"
                          .format(dev.name))
                    continue
                if not self.start:
                    self.start = f.most_recent_timestamp
                elif self.start > f.most_recent_timestamp:
                    self.start = f.most_recent_timestamp
                if f.metrics:
                    if f.most_recent_timestamp != dev.last_timestamp_written:
                        self.sds.to_sds(dev, f, f.most_recent_timestamp)
                        dev.last_t_stamp = f.most_recent_timestamp
                    else:
                        print("No new {} data".format(dev.get('device_name')))
            sleep(freq)
            i -= freq


def main():
    """Application's entry point"""
    config = ConfigParser()
    config.read("./config.ini")
    app = Program(config)
    app.run()


if __name__ == "__main__":
    main()
