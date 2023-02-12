import cv2
import mss
import numpy as np
import pyautogui
import pygetwindow
import sys
import time

from . import common
from . import freq_timer
from . import timer_pool
from . import state_pool

from .states import dead_state
from .states import init_process_state

CONFIG_KEY_LIST=[
    'process',
    'process_executable_path',
    'window_title',
    'fps',
]


class Runtime:

    def __init__(self, **kargs):
        self.init_kargs = kargs
        self.config_file = self.init_kargs['config_file']
        self.config_data = common.path_to_data(self.config_file)
        self.load_config_data(self)


    def load_config_data(self, o):
        for k in CONFIG_KEY_LIST:
            setattr(o, f'config_{k}', self.config_data[k])


    def run(self):
        self.timer_pool = timer_pool.TimerPool()
        self.state_pool = state_pool.StatePool()

        init_process_state.add_state(self.state_pool, self)
        dead_state.add_state(self.state_pool, self)
        self.state_pool.set_active('INIT_PROCESS')

        t0 = time.time()
        self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, self.config_fps, lambda sec: self.state_pool.tick(sec=sec, runtime=self)))

#         window = pygetwindow.getWindowsWithTitle(self.window_name)
#         assert(len(window)==1)
#         window = window[0]
#         window.activate()
#         self.window = window

#        w = window
#        self.window_box = {'top': w.top, 'left': w.left, 'width': w.width, 'height': w.height}

        self.sct = mss.mss()

        self.timer_pool.run()


instance = None

def run(**kargs):
    global instance
    instance = Runtime(**kargs)
    instance.run()