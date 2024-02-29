from DMD_main3 import control_DMD
import time
import serial
import generate_pattern
import pythoncolour

# Run Settings
type = "h" # Sampling type
order = "N" # Sampling order
width = 16 # width and height (16, 32, 64, 128, 256)
mode = 1 # number of images sampled (1 or 6)
grayscale = 255
size = width*width
arduino = pythoncolour.StreamArduino()



call_pattern = generate_pattern.DmdPattern(type, order, width, width, mode, grayscale)
hadamard_pattern, _ = call_pattern.execute()

cd = control_DMD(hadamard_pattern, project_name = "my_project",  main_sequence_itr=1, frame_time=100)
arduino.start()
cd.execute(0,width*width)
print("Getting data from Arduino...")
data = arduino.get_data(width*width)
print("GOT DATA:", data)
arduino.close()

