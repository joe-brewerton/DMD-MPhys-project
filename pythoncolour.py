# Python Script

import serial
import time

data_one = []

class StreamArduino:
    def __init__(self, port='COM3', baudrate=9600, timeout=1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def start(self):
        self.arduino.write(bytes("START", 'utf-8'))
        print("Arduino: START command sent")
        time.sleep(2)
        line = self.arduino.readline().decode().strip()
        print(line)

    def get_data(self, data_length):
        data_one = []
        time.sleep(2)
        for i in range(data_length):
            data_one.append(self.arduino.readline().decode().strip())
           
        self.arduino.write(bytes("STOP", 'utf-8'))

        return data_one
        
    def read_tcs_sensor(self):
        self.arduino.write(bytes("READ_TCS_SENSOR", 'utf-8'))  # Command Arduino to read sensor
        print("Python: Command sent to Arduino to read TCS sensor")
        data_one.append([self.arduino.readline().decode().strip()])

    def close(self):
        self.arduino.close()


