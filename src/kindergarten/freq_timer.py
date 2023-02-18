import time

class FreqTimer:

    def __init__(self, runtime, start, freq, func):
        self.runtime = runtime
        self.t0       = start
        self.freq     = freq
        self.func     = func
        self.tick_cnt = 1
        self.next_sec_cache = None
        self.update_next_sec_cache = True

    def next_sec(self, now_sec):
        if self.update_next_sec_cache:
            self.next_sec_cache = self.t0 + self.tick_cnt / self.freq
            if self.next_sec_cache < now_sec:
                self.t0 = now_sec
                self.tick_cnt = 0
                self.next_sec_cache = now_sec
            self.update_next_sec_cache = False
        return self.next_sec_cache

    def tick(self, now_sec):
        self.func(now_sec)
        self.tick_cnt += 1
        self.update_next_sec_cache = True
