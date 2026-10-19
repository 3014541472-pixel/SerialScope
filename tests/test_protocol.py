import unittest
from data_parser import parse_sensor_data
from serial_manager import SerialManager

class ProtocolTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_sensor_data('DEVICE_DATA,ID=12,VALUE=1.234\r\n'), {'sensor_id': 12, 'value': 1.234})
    def test_invalid(self):
        for frame in [None, '', 'TEMP:26.5', 'DEVICE_DATA,X=1,VALUE=2',
                      'DEVICE_DATA,ID=-1,VALUE=2', 'DEVICE_DATA,ID=1,VALUE=nan',
                      'DEVICE_DATA,ID=1,VALUE=1e999', 'DEVICE_DATA,ID=1,VALUE=2,EXTRA=3']:
            with self.subTest(frame=frame): self.assertIsNone(parse_sensor_data(frame))
    def test_loopback_fragments_and_recovery(self):
        manager = SerialManager()
        self.addCleanup(manager.disconnect)
        self.assertTrue(manager.connect('loop://')[0])
        manager.ser.write(b'DEVICE_DATA,ID=1,')
        self.assertEqual(manager.read_lines(), [])
        manager.ser.write(b'VALUE=2\r\nBAD\n')
        self.assertEqual(manager.read_lines(), ['DEVICE_DATA,ID=1,VALUE=2', 'BAD'])
        manager.ser.write(b'x' * 300 + b'\nDEVICE_DATA,ID=2,VALUE=3\n')
        self.assertEqual(manager.read_lines(), ['DEVICE_DATA,ID=2,VALUE=3'])
        manager.ser.write(b'partial')
        manager.read_lines()
        manager.disconnect()
        self.assertTrue(manager.connect('loop://')[0])
        self.assertTrue(manager.send_data('DEVICE_DATA,ID=3,VALUE=4'))
        self.assertEqual(manager.read_lines(), ['DEVICE_DATA,ID=3,VALUE=4'])
        manager.disconnect()
        self.assertFalse(manager.send_data('x'))
        self.assertEqual(manager.read_lines(), [])

if __name__ == '__main__': unittest.main()
