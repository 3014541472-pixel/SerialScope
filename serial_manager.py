
import serial
import serial.tools.list_ports


class SerialManager:
    """负责管理串口连接、发送和接收。"""

    def __init__(self):
        self.ser = None

    def list_ports(self):
        """扫描电脑当前可用的串口。"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self, port, baudrate=115200):
        """连接指定串口。"""
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )
            return True, f"Connected to {port}"
        except serial.SerialException as error:
            self.ser = None
            return False, str(error)

    def disconnect(self):
        """断开串口。"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def send_data(self, message):
        """发送文本数据。"""
        if self.ser and self.ser.is_open:
            self.ser.write(message.encode("utf-8"))
            return True
        return False

    def read_data(self):
        """读取当前收到的数据。"""
        if self.ser and self.ser.is_open:
            data = self.ser.readline()
            return data.decode("utf-8", errors="replace").strip()
        return ""
