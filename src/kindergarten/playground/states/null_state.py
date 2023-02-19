class NullState:

    def __init__(self,runtime,**kwargs):
        self.id = 'NULL'
        self.runtime = runtime
        self.kwargs = kwargs
        self.config = runtime.config

    def tick(self, **kwargs):
        pass

    def on_active(self, **kwargs):
        pass

    def on_inactive(self, **kwargs):
        pass

    def next_sec(self, **kwargs):
        return None
