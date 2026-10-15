from data_parser import parse_sensor_data

tests = [
    "DEVICE_DATA,ID=1,VALUE=26.50",
    "DEVICE_DATA,ID=2,VALUE=abc",
    "BAD_DATA,ID=3,VALUE=20.0",
    "DEVICE_DATA,ID=4",
]

for item in tests:
    result = parse_sensor_data(item)
    print(item, "->", result)