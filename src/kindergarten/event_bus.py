import heapq
import time
import types

ns = types.SimpleNamespace

class EventBus:

    def __init__(self, runtime):
        self.runtime = runtime
    
        self.listener_id_to_ns_dict={}
        self.event_type_id_to_ns_dict={}
        
        self.event_call_queue = []

    def add_listener(self, event_type_id, callable, listener_id=None, priority=0, ret_id=None):
        if listener_id == None:
            listener_id = f'_AUTO_{self.runtime.auto_id()}'
        else:
            self.rm_listener(listener_id)
        
        listener_ns = ns()
        listener_ns.listener_id   = listener_id
        listener_ns.order_id      = self.runtime.auto_id()
        listener_ns.event_type_id = event_type_id
        listener_ns.callable      = callable
        listener_ns.priority      = priority
        listener_ns.ret_id        = ret_id
        self.listener_id_to_ns_dict[listener_id] = listener_ns

        event_type_ns = self._get_event_type_ns(event_type_id, prepare_listener_ns_list=False)
        event_type_ns.listener_id_set.add(listener_id)
        event_type_ns.listener_ns_list = None

    def rm_listener(self, listener_id):
        if listener_id not in self.listener_id_to_ns_dict:
            return
        listener_ns = self.listener_id_to_ns_dict[listener_id]
        del self.listener_id_to_ns_dict[listener_id]

        event_type_ns = self._get_event_type_ns(listener_ns.event_type_id, prepare_listener_ns_list=False)
        event_type_ns.listener_id_set.remove(listener_id)
        event_type_ns.listener_ns_list = None

    def call_sync(self, event_type_id, kwargs={}):
        ret = {}
        event_type_ns = self._get_event_type_ns(event_type_id, prepare_listener_ns_list=True)
        for listener_ns in event_type_ns.listener_ns_list:
            ret0 = listener_ns.callable(**kwargs)
            if listener_ns.ret_id is not None:
                ret[listener_ns.ret_id] = ret0
        return ret

    def call_async(self, event_type_id, kwargs={}, callback=None, t=time.time()):
        tt = min(t,time.time())
        with self.runtime.main_lock:
            heapq.heappush(self.event_call_queue,(
                tt,self.runtime.auto_id(),
                self._call_async0,
                {
                    'event_type_id': event_type_id,
                    'kwargs': kwargs,
                    'callback':callback,
                    't':t,
                },
            ))
        self.runtime.notify()

    def _call_async0(self, event_type_id, kwargs, callback, t):
        ret_dict = {}
        event_type_ns = self._get_event_type_ns(event_type_id, prepare_listener_ns_list=True)
        for listener_ns in event_type_ns.listener_ns_list:
            with self.runtime.main_lock:
                heapq.heappush(self.event_call_queue,(
                    t, self.runtime.auto_id(),
                    self._call_async1,
                    {
                        'listener_ns' : listener_ns,
                        'kwargs' : kwargs,
                        'ret_dict' : ret_dict,
                    },
                ))
        if callback is not None:
            with self.runtime.main_lock:
                heapq.heappush(self.event_call_queue,(
                    t, self.runtime.auto_id(),
                    self._call_async2,
                    {
                        'callback' : callback,
                        'ret_dict' : ret_dict,
                    },
                ))

    def _call_async1(self, listener_ns, kwargs, ret_dict):
        ret0 = listener_ns.callable(**kwargs)
        if listener_ns.ret_id is not None:
            ret_dict[listener_ns.ret_id] = ret0

    def _call_async2(self, callback, ret_dict):
        callback(ret_dict)

    def run_loop(self):
        while self.runtime.is_running():
            if len(self.event_call_queue) <= 0:
                with self.runtime.main_lock:
                    self.runtime.running_wait()
                    continue
            now_sec = time.time()
            run_sec = self.event_call_queue[0][0]
            if now_sec < run_sec:
                self.runtime.running_wait(run_sec-now_sec)
                continue
            self.run_tick(now_sec)

    def run_tick(self,now_sec):
        if len(self.event_call_queue) <= 0: return
        run_sec = self.event_call_queue[0][0]
        if now_sec < run_sec: return
        _,_,f,kwargs = heapq.heappop(self.event_call_queue)
        f(**kwargs)

    def _get_event_type_ns(self, event_type_id, prepare_listener_ns_list):
        if event_type_id not in self.event_type_id_to_ns_dict:
            event_type_ns = ns()
            event_type_ns.listener_id_set = set()
            event_type_ns.listener_ns_list = None
            self.event_type_id_to_ns_dict[event_type_id] = event_type_ns
        else:
            event_type_ns = self.event_type_id_to_ns_dict[event_type_id]

        if prepare_listener_ns_list and event_type_ns.listener_ns_list is None:
            listener_ns_list = event_type_ns.listener_id_set
            listener_ns_list = map(lambda i:self.listener_id_to_ns_dict[i], listener_ns_list)
            listener_ns_list = sorted(listener_ns_list, key=lambda i:(i.priority,i.order_id))
            event_type_ns.listener_ns_list = listener_ns_list

        return event_type_ns
