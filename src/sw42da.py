import os

import serial

from dotenv import load_dotenv

load_dotenv()
HOST_IP = os.getenv("HOST_IP")
HOST_PORT = os.getenv("HOST_PORT")
HOST_BAUDRATE = os.getenv("HOST_BAUDRATE", "57600")


class Sw42da:

    def __init__(self):
        self._url = f"socket://{HOST_IP}:{HOST_PORT}"


    async def send_command(self, c: str):

        if not c.endswith("\n"):
            c = c + "\n"

        b = bytes(c, "UTF-8")

        ser = serial.serial_for_url(url=self._url, stopbits=1, bytesize=8, baudrate=HOST_BAUDRATE, parity="N", timeout=0.5)
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