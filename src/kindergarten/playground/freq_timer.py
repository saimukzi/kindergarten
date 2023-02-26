import time

class FreqCallSyncTimer:

    def __init__(self, runtime, freq, event_type_id):
        self.runtime       = runtime
        self.freq          = freq
        self.event_type_id = event_type_id
        self.enable        = False
        self.my_id   = f'_FreqCallSyncTimer.{runtime.auto_id()}'
        self.runtime.event_bus.add_listener(self.my_id, self.on_EV, listener_id=self.my_id)

    def set_enable(self, enable, t0=time.time(), **kwargs):
        self.enable   = enable
        if self.enable:
            self.session_id = self.runtime.auto_id()
            self.t0       = t0
            self.tick_cnt = 0
            self.runtime.call_async(self.my_id, kwargs={'session_id':self.session_id}, t=t0)

    def on_EV(self, now_sec, session_id, **kwargs):
        if not self.enable: return
        if session_id != self.session_id: return
        self.runtime.call_sync(self.event_type_id, now_sec=now_sec)
        now_sec0 = time.time()
        self.tick_cnt+=1
        next_sec = self.t0 + self.tick_cnt / self.freq
        if next_sec < now_sec0:
            next_sec = now_sec0
            self.t0 = now_sec0
            self.tick_cnt = 0
        self.runtime.call_async(self.my_id, kwargs={'session_id':session_id}, t=next_sec)
