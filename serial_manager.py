"""Bounded, nonblocking newline-framed serial input for Tkinter polling."""
import serial
from serial.tools import list_ports


class SerialManager:
    MAX_FRAME = 256

    def __init__(self):
        self.ser = None
        self.buffer = bytearray()
        self.discarding = False

    def list_ports(self):
        return [p.device for p in list_ports.comports()]

    @property
    def connected(self):
        return self.ser is not None and self.ser.is_open

    def connect(self, port, baudrate=115200):
        self.disconnect()
        try:
            # serial_for_url also enables loop:// for tests without a board.
            self.ser = serial.serial_for_url(port, baudrate=int(baudrate), timeout=0,
                                             write_timeout=0.2)
            return True, f"Connected to {port}"
        except (serial.SerialException, ValueError, OSError) as error:
            return False, str(error)

    def disconnect(self):
        try:
            if self.ser is not None:
                self.ser.close()
        finally:
            self.ser = None
            self.buffer.clear()
            self.discarding = False

    def read_lines(self):
        if not self.connected:
            return []
        chunk = self.ser.read(min(self.ser.in_waiting, 4096))
        lines = []
        for byte in chunk:
            if byte == 10:
                if not self.discarding:
                    lines.append(self.buffer.decode('utf-8', errors='replace').rstrip('\r'))
                self.buffer.clear()
                self.discarding = False
            elif not self.discarding:
                self.buffer.append(byte)
                if len(self.buffer) > self.MAX_FRAME:
                    self.buffer.clear()
                    self.discarding = True
        return lines

    def send_data(self, message):
        if not self.connected:
            return False
        payload = (message.rstrip('\r\n') + '\n').encode('utf-8')
        if self.ser.write(payload) != len(payload):
            raise serial.SerialTimeoutException('Incomplete serial write')
        return True
