import cv2
import numpy as np
import sys
import threading
import time
import traceback

from kindergarten import common

from . import console
from . import event_bus
from . import focus
from . import freq_timer
from . import hotkey
# from . import keyboard_capture
from . import monkey
from . import process_pool
from . import screen_capture
from . import screen_recorder
from . import screen_sample_tools
from . import state_pool
from . import thread_pool

from .states import common_state
from .states import dead_state
from .states import init_process_state

from kindergarten.hina.holocure import holocurebot

class Runtime:

    def __init__(self, cmd_args):
        self.init_cmd_args = cmd_args
        self.config_file = self.init_cmd_args.config_file
        self.config = common.read_config(self.config_file)

        self.last_auto_id = 1
        self.var_dict = {}

    def run(self):
        self.running = True
    
        self.main_lock = threading.Condition()
        self.thread_pool = thread_pool.ThreadPool(self)
        
        self.event_bus  = event_bus.EventBus(self)
        #process_pool.init(self)
        self.process_pool = process_pool.ProcessPool(self)
        # self.timer_pool = timer_pool.TimerPool()
        self.state_pool = state_pool.StatePool(self)

        dead_state.add_state(self.state_pool, self)
        self.state_pool.add_state(common_state.IdleState(self))
        self.state_pool.set_active('IDLE')
        # self.timer_pool.add_timer(self.state_pool)

        t0 = time.time()
        # self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, self.config.fps, lambda sec: self.state_pool.tick(sec=sec, runtime=self)))

        # self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, self.config.fps, self.console.tick))
        # self.timer_pool.add_timer(self.console)
        
        self.screen_capture = screen_capture.ScreenCapture(self)
        # self.timer_pool.add_timer(self.screen_capture.freq_timer)
        
        self.screen_recorder = screen_recorder.ScreenRecorder(self)
        # self.keyboard_capture = keyboard_capture.KeyboardCapture(self)
        
#         window = pygetwindow.getWindowsWithTitle(self.window_name)
#         assert(len(window)==1)
#         window = window[0]
#         window.activate()
#         self.window = window

#        w = window
#        self.window_box = {'top': w.top, 'left': w.left, 'width': w.width, 'height': w.height}

        # self.sct = mss.mss()

        self.event_bus.add_listener('EXIT', self.on_EXIT_INF, priority=common.INF)

        self.focus = focus.Focus(self)
        
        self.screen_sample_tools = screen_sample_tools.ScreenSampleTools(self)
        
        self.monkey = monkey.Monkey(self)
        
        self.holocurebot = holocurebot.HoloCureBot(self)
        
        self.hotkey = hotkey.Hotkey(self)

        self.console = console.Console(self)
        self.console.start()

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

    def call_async(self, *args, **kwargs):
        return self.event_bus.call_async(*args, **kwargs)

    def call_sync(self, *args, **kwargs):
        return self.event_bus.call_sync(*args, **kwargs)

    def on_EXIT_INF(self, **kwargs):
        self.stop()

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

def run(cmd_args):
    global instance
    instance = Runtime(cmd_args)
    instance.run()
