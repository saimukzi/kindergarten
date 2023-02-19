import cv2
import numpy as np
import sys
import threading
import time
import traceback

from . import common
from . import console
from . import event_bus
from . import freq_timer
# from . import timer_pool
from . import screen_capture
from . import state_pool

from .states import common_state
from .states import dead_state
from .states import init_process_state

# CONFIG_KEY_LIST=[
#     'fps',
#     'process',
#     'process_executable_path',
#     'screen_record_path',
#     'window_title',
# ]


class Runtime:

    def __init__(self, **kargs):
        self.init_kargs = kargs
        self.config_file = self.init_kargs['config_file']
        self.config = common.path_to_namespace(self.config_file)

        self.last_auto_id = 1
        self.var_dict = {}

    def run(self):
        self.running = True
    
        self.main_lock = threading.Condition()
        self.event_bus  = event_bus.EventBus(self)
        # self.timer_pool = timer_pool.TimerPool()
        self.state_pool = state_pool.StatePool(self)

        dead_state.add_state(self.state_pool, self)
        self.state_pool.add_state(common_state.IdleState(self))
        self.state_pool.set_active('IDLE')
        # self.timer_pool.add_timer(self.state_pool)

        t0 = time.time()
        # self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, self.config.fps, lambda sec: self.state_pool.tick(sec=sec, runtime=self)))

        self.console = console.Console(self)
        self.console.start()
        # self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, self.config.fps, self.console.tick))
        # self.timer_pool.add_timer(self.console)
        
        # self.screen_capture = screen_capture.ScreenCapture(self)
        # self.timer_pool.add_timer(self.screen_capture.freq_timer)

#         window = pygetwindow.getWindowsWithTitle(self.window_name)
#         assert(len(window)==1)
#         window = window[0]
#         window.activate()
#         self.window = window

#        w = window
#        self.window_box = {'top': w.top, 'left': w.left, 'width': w.width, 'height': w.height}

        # self.sct = mss.mss()

        try:
            self.event_bus.run_loop()
        except:
            traceback.print_exc()
        finally:
            self.stop()
            self.console.join()


    def stop(self):
        with self.main_lock:
            self.running = False
            self.main_lock.notify_all()

    def wait(self, timeout=None):
        with self.main_lock:
            self.main_lock.wait(timeout=timeout)

    def running_wait(self, timeout=None):
        with self.main_lock:
            if not self.running: return
            self.main_lock.wait(timeout=timeout)

    def notify(self):
        with self.main_lock:
            self.main_lock.notify_all()

    def is_running(self):
        with self.main_lock:
            return self.running

    def auto_id(self):
        with self.main_lock:
            self.last_auto_id += 1
            return self.last_auto_id


instance = None

def run(**kargs):
    global instance
    instance = Runtime(**kargs)
    instance.run()
