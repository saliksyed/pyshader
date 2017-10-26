import pyaudio
import wave
import numpy as np
from threading import Thread

class Audio:
    def __init__(self, file, paused=False):
        self.tick = 0
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()

        # open stream based on the wave object which has been input.
        self.stream = self.p.open(format =
                        self.p.get_format_from_width(self.wf.getsampwidth()),
                        channels = self.wf.getnchannels(),
                        rate = self.wf.getframerate(),
                        output = True)
        self.audio_thread =  Thread(target = self.play_frame)
        self.data = self.wf.readframes(1024)
        self.peak = 0
        self.level = 0
        self.paused = paused
        self.audio_thread.start()

    def pause(self):
        self.paused = True

    def play(self):
        self.paused = False

    def play_frame(self):
        while self.data != '':
            if self.paused:
                continue
            parsed = np.fromstring(self.data,dtype=np.int16)
            peak=np.average(np.abs(parsed))*2
            self.level = float(50*peak/2**16)
            self.stream.write(self.data)
            self.data = self.wf.readframes(1024)

    def get_level(self):
        return self.level

    def process(self, fn):
        return fn(self.data)
