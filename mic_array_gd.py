#!/usr/bin/env python3

## FILE: mic_array.py
## 
import pyaudio
import time
import threading
import numpy as np
import math
import random

try:
    # python2 
    import Queue
except:
    # python3
    import queue as Queue

SOUND_SPEED=343.2
fs=16000
MIC_DISTANCE_6P1=0.064
MAX_TDOA_6P1=MIC_DISTANCE_6P1 / float(SOUND_SPEED)
NFFT = 1024

class MicArray(object):

    def __init__(self, rate = fs, channels=8, chunk_size=None):
        self.pyaudio_instance = pyaudio.PyAudio()
        self.queue = Queue.Queue()
        self.sep_queue = Queue.Queue()
        self.quit_event = threading.Event()
        self.channels = channels
        self.sample_rate = rate
        self.chunk_size =  NFFT #chunk_size if chunk_size else rate / NFFT
        self.df = rate / NFFT
       
        device_index = None
        for i in range(self.pyaudio_instance.get_device_count()):
            dev = self.pyaudio_instance.get_device_info_by_index(i)
            name = dev['name'].encode('utf-8')
            print(i, name, dev['maxInputChannels'], dev['maxOutputChannels'])
            if dev['maxInputChannels'] == self.channels:
                print('Use {}'.format(name))
                device_index = i
                break

        if device_index is None:
            raise Exception('can not find input device with {} channel(s)'.format(self.channels))


        self.stream = self.pyaudio_instance.open(
            input=True,
            start=False,
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=int(self.sample_rate),
            frames_per_buffer=int(self.chunk_size),
            stream_callback=self._callback,
            input_device_index=device_index,
        )

        ## build GD matrix
        mic_theta = np.arange(0, 2*np.pi, 2*np.pi/6)
        # 0,0 is the middle one mic in uca
        a = np.cos(mic_theta)
        b = np.sin(mic_theta)
        self.GD_matrix = np.zeros((3,7))
        for i in range(1,7,1):
            self.GD_matrix[0,i] = a[i-1]
            self.GD_matrix[1,i] = b[i-1]
        #
        #boundary_max_theta = 360
        #boundary_max_phi = 90
        #boundary_min = 0
        #grid_section = 30
        #swarm position
        self.swarm = np.zeros((22, 3))
        theta_grid = np.ones(11)*range(30, 360, 30)
        phi_grid = np.ones(2)*range(30, 90, 30)
        for i in range(0,11):
            self.swarm[i] = np.array([theta_grid[i], phi_grid[0], 0])
            self.swarm[i+11] = np.array([theta_grid[i], phi_grid[1], 0])


    def _callback(self, in_data, frame_count, time_info, status):
        self.queue.put(in_data)
        return None, pyaudio.paContinue

    def start(self):
        self.queue.queue.clear()
        self.stream.start_stream()


    def read_chunks(self):
        self.quit_event.clear()
        while not self.quit_event.is_set():
            frames = self.queue.get()
            if not frames:
                break

            yield frames

    def stop(self):
        self.quit_event.set()
        self.stream.stop_stream()
        self.queue.put('')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if value:
            return False
        self.stop()

    def spilt (buf)
        Buff = np.zeros((7, len(buf)//8))
        for i in range(0,7,1):
        Buff[i] = buf[i::8]
    return Buff

    def cost(angle, Buff, self):
        cost = 0.
        frqs = np.arange(0.,self.sample_rate/2 + self.df, self.df)
        w = 2*np.pi* frqs
        k = w / 343#    k = w / SOUND_SPEED
        kappa = np.array([math.cos(angle[1])*math.cos(angle[0]), math.cos(angle[1])*math.sin(angle[0]), math.sin(angle[1])])
        W = np.fft.rfft(Buff,1024)
        W = W.T.conj()
        for i in range(0,len(frqs)-1):
            a = np.exp(1j*k[i])*(np.matmul(kappa,self.GD_matrix))
            y = abs(np.matmul(W[i],a))
            cost = cost + y
        return cost

    def get_direction(self, buf):
        Buff = spilt(buf)
        iterations = 5
        mu = 0.2
        swarms = 22
        M = 2        
        delta = np.array([[0.005, 0.], [0., 0.005]])
        gradient = np.array([[0.,0.]])

        for times in range(0, iterations):
            for k in range(0, swarms):
                for dim in range(0, M):
                    gradient[0,dim] = (cost(swarm[k,0:M] + delta[dim], Buff, self)- cost(swarm[k,0:M], Buff, self) ) /0.005
                    swarm[k, dim] = swarm[k, dim]+ mu*gradient[0,dim]*random.random()
                swarm[k, M] = cost(swarm[k,0:M], Buff, self) 
                                                   
        A = np.array([swarm[:,M]])
        best = np.argmax(A)
        C = self.swarm[best,0:2]
        return   np.array([C])

def test_8mic():
    import signal
    import time
    from pixel_ring import pixel_ring

    is_quit = threading.Event()
    

    def signal_handler(sig, num):
        is_quit.set()
        print('Quit')

    signal.signal(signal.SIGINT, signal_handler)
 
    en_speech = np.zeros((1,))
    raw = np.zeros((1, 8))
    with MicArray(16000, 8, 1024)  as mic:
        for frames in mic.read_chunks():
            chunk = np.fromstring(frames, dtype='int16')
            direction = mic.get_direction(chunk)            
            pixel_ring.set_direction(direction[0])
            print('@ {:.2f}'.format(direction))\

            if is_quit.is_set():
                break
                
    pixel_ring.off()
    return raw, en_speech


if __name__ == '__main__':
    # test_4mic()
    raw, en_speech = test_8mic()
