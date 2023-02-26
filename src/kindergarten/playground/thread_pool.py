import collections
import concurrent.futures as cf
import traceback
import types

SN = types.SimpleNamespace
deque = collections.deque

class ThreadPool:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config

        self.thread_pool_executor = cf.ThreadPoolExecutor()
        
        self.map = self.thread_pool_executor.map

    def filter_uo(self, func, itr):
        o = SN()
        o.func   = func
        o.itr    = itr
        o.q      = deque()
        o.done0  = False
        o.fire1  = 0
        o.done1  = 0
        
        # create a single thread, to put itr to func
        self.thread_pool_executor.submit(self._filter0,o)

        # wait func output, yield
        while True:
            with self.runtime.main_lock:
                q_len = len(o.q)
            if q_len > 0:
                with self.runtime.main_lock:
                    v = o.q.popleft()
                yield v
                continue
            with self.runtime.main_lock:
                if len(o.q) > 0: continue
                if o.done0 and (o.fire1==o.done1): break
                # print('SMJGJGMPBT wait')
                self.runtime.main_lock.wait()

    def _filter0(self, o):
        try:
            #print('_filter0 JYDMGRBYZW')
            for v in o.itr:
                #print(f'_filter0 LERRHATMRQ {v}')
                o.fire1 += 1
                self.thread_pool_executor.submit(self._filter1,o,v)
            with self.runtime.main_lock:
                o.done0 = True
                self.runtime.main_lock.notify_all()
        except:
            traceback.print_exc()
            self.runtime.stop()

    def _filter1(self, o, v):
        try:
            #print(f'_filter1 ZVKOVRJGEF {v}')
            b = o.func(v)
            with self.runtime.main_lock:
                if b:
                    o.q.append(v)
                o.done1 += 1
                self.runtime.main_lock.notify_all()
        except:
            traceback.print_exc()
            self.runtime.stop()
