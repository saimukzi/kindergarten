import mss
import time
import pygetwindow

from . import freq_timer

class ScreenCapture:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        self.freq_timer = freq_timer.FreqTimer(self.runtime, time.time(), self.config.fps, self.tick)
        self.sct = mss.mss()

        self.enable = False

    def set_enable(self, enable, **kwargs):
        if enable:
            w = pygetwindow.getWindowsWithTitle(self.config.window_title)
            assert(len(w)==1)
            w = w[0]
            self.window_box = {'top': w.top, 'left': w.left, 'width': w.width, 'height': w.height}

        self.enable = enable
        self.freq_timer.set_enable(enable=enable, **kwargs)

    def tick(self, now_sec, **kwargs):
        print('SDJSCRAFHV ScreenShotState.tick')
        if not self.enable: return
        
        screen = self.runtime.sct.shot()
