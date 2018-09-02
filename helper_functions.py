from datetime import datetime
"""
helper_functions: contains output and error handling methods
"""


def cleanup_single(client, namespace_id, type_id):
    """Deletes streams and types related to a type id"""
    print("Deleting stream, '{}'".format(type_id))
    supress_error(lambda: client.delete_stream(namespace_id, type_id))
    print("Deleting type, '{}'".format(type_id))
    supress_error(lambda: client.delete_type(namespace_id, type_id))


def raise_error(client, namespace_id, type_ids, message, exception=Exception):
    """Custom raise that also cleanups up types and streams"""
    cleanup(client, namespace_id, type_ids)
    raise exception(message)


def cleanup(client, namespace_id, type_ids):
    """Deletes streams and types related to parameter type names"""
    for type_id in type_ids:
        cleanup_single(client, namespace_id, type_id)


def to_string(event):
    """Outputs an SdsTypeData object in string format"""
    string = ""
    for k, v in event.__dict__.items():
        if k != 'type_id' and k != 'prop_names':
            if k == 'time':
                string = "{}: {}".format(v, string)
            elif v is None:
                string += "{}: , ".format(k)
            else:
                string += "{}: {}, ".format(k, v)
    return string[:-2]


def supress_error(sds_call):
    """Custom error handler when an sds call fails"""
    try:
        sds_call()
    except Exception as e:
        print(("Encountered Error: {error}".format(error=e)))


def seconds_to_iso(n):
    """Converts seconds from string format to ISO format"""
    if type(n) not in (int, float):
        raise ("{} must be types, int or float but is {}".format(n, type(n)))
    return datetime.utcfromtimestamp(n)


def datetime_to_int_seconds(dt_obj):
    """Converts a datetime object to integer seconds"""
    epoch_start = datetime(1970, 1, 1)
    if type(dt_obj) is not datetime:
        raise ('{} must be type, datetime but is {}'.format(dt_obj,
                                                            type(dt_obj)))

    return int((dt_obj - epoch_start).total_seconds())


def print_feed(feed):
    """Converts a weather station feed into user-readable format"""
    if not feed:
        return -1
    for k, v in feed.items():
        unit = v.get("unit")
        unit_dict = {"degrees_celsius": "C",
                     "kilometers_per_hour": "kph",
                     "millimeters": "mm"}

        if unit in unit_dict:
            unit = unit_dict[unit]
        unit = unit.replace("_", " ")
        print("{} ({})".format(k, unit))
        print("=" * (len(k) + len(unit) + 3))
        events = v.get('values')
        for event in events:
            date_time = datetime.fromtimestamp(
                int(event.get("u"))
            ).strftime('%Y-%m-%d %H:%M:%S')
            value = event.get("s")
            print("{}: {} {}".format(date_time, value, unit))
        return 0
