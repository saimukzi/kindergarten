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
            w = filter(lambda i:i.title==self.config.window_title,w)
            if hasattr(self.config, 'window_width'):
                w = filter(lambda i:i.width==self.config.window_width,w)
            if hasattr(self.config, 'window_height'):
                w = filter(lambda i:i.height==self.config.window_height,w)
            w = list(w)
            #assert(len(w)==1)
            if len(w) != 1:
                for ww in w:
                    print(ww)
                assert(False)
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
        screen_shot = screen_shot[:,:,:3]

        # print(screen_shot.shape)
        
        self.runtime.event_bus.call_async('SCREEN_CAPTURE_IMG', {'screen_shot':screen_shot,'capture_sec':capture_sec})
