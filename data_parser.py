"""SerialScope wire protocol: DEVICE_DATA,ID=<sequence>,VALUE=<number> LF."""
import math
import re

FRAME = re.compile(r'DEVICE_DATA,ID=([0-9]+),VALUE=([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)')


def parse_sensor_data(data):
    if not isinstance(data, str) or len(data) > 256:
        return None
    match = FRAME.fullmatch(data.strip())
    if match is None:
        return None
    try:
        sequence, value = int(match[1]), float(match[2])
        if not math.isfinite(value):
            return None
        return {'sensor_id': sequence, 'value': value}
    except ValueError:
        return None
