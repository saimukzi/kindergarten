import mss
import numpy
import time
import pygetwindow

from . import freq_timer

class ScreenCapture:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        self.sct = mss.mss()
        self.freq_timer = freq_timer.FreqCallSyncTimer(runtime, runtime.config.fps, 'SCREEN_CAPTURE_TICK')

        self.enable = False
        
        self.runtime.event_bus.add_listener('SCREEN_CAPTURE_TICK', self.on_SCREEN_CAPTURE_TICK)

    def set_enable(self, enable, **kwargs):
        if enable:
            w = pygetwindow.getWindowsWithTitle(self.config.window_title)
            assert(len(w)==1)
            w = w[0]
            if hasattr(self.config,'screen_chop'):
                sc = self.config.screen_chop
                self.window_box = {
                    'top': w.top+sc.y0, 'left': w.left+sc.x0,
                    'width': sc.width, 'height': sc.height,
                }
            else:
                self.window_box = {'top': w.top, 'left': w.left, 'width': w.width, 'height': w.height}

        self.enable = enable
        self.freq_timer.set_enable(enable=enable, **kwargs)

    def on_SCREEN_CAPTURE_TICK(self, **kwargs):
        # print('SDJSCRAFHV ScreenShotState.tick')
        if not self.enable: return
        
        capture_sec = time.time()
        screen_shot = self.sct.grab(self.window_box)
        screen_shot = numpy.array(screen_shot)
        screen_shot = screen_shot[:,:,[2,1,0]]

        # print(screen_shot.shape)
        
        self.runtime.event_bus.call_async('SCREEN_CAPTURE_IMG', {'screen_shot':screen_shot,'capture_sec':capture_sec})
