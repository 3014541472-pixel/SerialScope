data = "TEMP:26.5"
#split the string
parts=data.split(":")
#extract the value
temperature=float(parts[1])
print("received data:",data)
print("temperature:",temperature)
print("data tape:",type(temperature))