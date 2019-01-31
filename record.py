import pyaudio
import wave
import sys
import numpy
import struct
#import scipy
#sys.path.append("/sdk/dualfisheye-to-affectiva-master/scipy-master/scipy/io")
#import wavfile
#import numpy
#import matplotlib.pyplot as plt


RESPEAKER_RATE = 32000 
RESPEAKER_CHANNELS = 8 # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 2  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 1
WAVE_OUTPUT_FILENAME = "output1.wav"

p = pyaudio.PyAudio()

stream = p.open(
            rate=RESPEAKER_RATE,
            format=p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            input_device_index=RESPEAKER_INDEX,)

print("* recording")

frames = []

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wave_data = numpy.fromstring(b''.join(frames), dtype = '<i2')
wave_data.shape = -1, RESPEAKER_CHANNELS
wave_data = wave_data.T
wave_data = wave_data
print('wave_data:\n', wave_data,'dimesion : 8 X',wave_data.size/8)
numpy.savetxt('output_data.txt',wave_data,fmt = '%d')


