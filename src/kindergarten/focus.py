import pygetwindow
import traceback

class Focus:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
    
    def focus(self):
        window = pygetwindow.getWindowsWithTitle(self.config.window_title)
        assert(len(window)==1)
        window = window[0]

        window.restore()
        window.activate()
