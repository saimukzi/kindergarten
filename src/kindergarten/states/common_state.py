import copy
import os
import wmi

from . import null_state

class WaitState(null_state.NullState):

    def __init__(self,id,timeout,next_id,runtime):
        super().__init__(runtime)
        self.id = id
        self.timeout = timeout
        self.next_id = next_id

    def on_active(self, now_sec, **kwargs):
        self.end_sec = self.timeout+now_sec

    def tick(self, now_sec, **kwargs):
        if now_sec<self.end_sec: return
        self.runtime.state_pool.set_active(self.next_id)


class WaitUntilState(null_state.NullState):

    def __init__(self,id,func,pos_id,timeout,neg_id,runtime):
        super().__init__(runtime)
        self.id = id
        self.func = func
        self.pos_id = pos_id
        self.timeout = timeout
        self.neg_id = neg_id

    def on_active(self, now_sec, **kwargs):
        self.end_sec = self.timeout+now_sec

    def tick(self, now_sec, **kwargs):
        if self.func(now_sec=now_sec, runtime=self.runtime, state=self, **kwargs):
            self.runtime.state_pool.set_active(self.pos_id)
        if now_sec<self.end_sec: return
        self.runtime.state_pool.set_active(self.neg_id)


class TransState(null_state.NullState):

    def __init__(self,id,next_id,runtime):
        super().__init__(runtime)
        self.id = id
        self.next_id = next_id

    def tick(self, state_kwargs, **kwargs):
        self.runtime.state_pool.set_active(self.next_id, state_kwargs=state_kwargs)


class FuncState(null_state.NullState):

    def __init__(self,id,func,runtime):
        super().__init__(runtime)
        self.id = id
        self.func = func

    def tick(self, **kwargs):
        self.func(runtime=self.runtime, state=self, **kwargs)


class IdleState(null_state.NullState):
    def __init__(self, runtime):
        super().__init__(runtime)
        self.id = 'IDLE'


# class DieState(null_state.NullState):
# 
#     def __init__(self,id,runtime):
#         super().__init__(runtime)
#         self.id = id
# 
#     def tick(self, **kwargs):
#         assert(False)
