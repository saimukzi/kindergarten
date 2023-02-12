import time

class FreqTimer:

    def __init__(self, runtime, start, freq, func):
        self.runtime = runtime
        self.t0       = start
        self.freq     = freq
        self.func     = func
        self.tick_cnt = 1

    def next_sec(self):
        return self.t0 + self.tick_cnt / self.freq

    def update_next_sec(self, sec):
        self.tick_cnt += 1
        if self.next_sec() < sec:
            self.t0 = sec
            self.tick_cnt = 0

    def run(self, sec):
        self.func(sec)
