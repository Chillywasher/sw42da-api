import os
import json
import serial

from dotenv import load_dotenv

load_dotenv()

if os.path.isfile("/data/options.json"):
    json_path = "/data/options.json"
elif os.path.isfile("data/options.json"):
    json_path = "data/options.json"
else:
    raise Exception("Unable to load config options!")

with open(json_path) as f:
    config = json.load(f)

print(config)

HOST_IP = config["HOST_IP"]
HOST_PORT = config["HOST_PORT"]
HOST_BAUDRATE = config["HOST_BAUDRATE"]

if not HOST_IP:
    raise Exception("Could not load HOST_IP variable")


class Sw42da:

    def __init__(self):
        self._url = f"socket://192.168.67.31:8000"

    async def send_command(self, c: str):

        if not c.endswith("\n"):
            c = c + "\n"

        b = bytes(c, "UTF-8")

        ser = serial.serial_for_url(url=self._url, stopbits=1, bytesize=8, baudrate=57600, parity="N", timeout=0.5)
        ser.write(b)

        response = []
        while True:
            line = ser.readline()
            if line:
                string = line.decode()
                response.append(string)
                if line == b'SW42DA>':
                    break
            else:
                break

        ser.close()

        return response