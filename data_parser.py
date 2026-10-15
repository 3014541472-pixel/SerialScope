
def parse_sensor_data(data):
    """
    Parse sensor data received from a device.

    Expected format:
    DEVICE_DATA,ID=1,VALUE=26.50
    """

    try:
        parts = data.strip().split(",")

        if len(parts) != 3:
            return None

        if parts[0] != "DEVICE_DATA":
            return None

        sensor_id = int(parts[1].split("=")[1])
        value = float(parts[2].split("=")[1])

        return {
            "sensor_id": sensor_id,
            "value": value
        }

    except (ValueError, IndexError):
        return None


if __name__ == "__main__":
    test_data = "DEVICE_DATA,ID=8,VALUE=32.75"

    result = parse_sensor_data(test_data)

    if result:
        print("Sensor ID:", result["sensor_id"])
        print("Sensor Value:", result["value"])
    else:
        print("Invalid data")
