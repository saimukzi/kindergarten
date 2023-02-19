import time

class FreqTimer:

    def __init__(self, runtime, start, freq, func):
        self.runtime = runtime
        self.freq    = freq
        self.func    = func
        self.enable  = False
        self.update_next_sec_cache = True

    def set_enable(self, enable, t0=time.time(), **kwargs):
        self.enable   = enable
        self.update_next_sec_cache = True
        if self.enable:
            self.t0       = t0
            self.tick_cnt = 1
            self.next_sec_cache = None
            self.runtime.notify()

    def next_sec(self, now_sec):
        if self.update_next_sec_cache:
            if self.enable:
                self.next_sec_cache = self.t0 + self.tick_cnt / self.freq
                if self.next_sec_cache < now_sec:
                    self.t0 = now_sec
                    self.tick_cnt = 0
                    self.next_sec_cache = now_sec
            else:
                self.next_sec_cache = None
            self.update_next_sec_cache = False
        return self.next_sec_cache

    def tick(self, now_sec):
        if self.enable:
            self.func(now_sec)
        self.tick_cnt += 1
        self.update_next_sec_cache = True
