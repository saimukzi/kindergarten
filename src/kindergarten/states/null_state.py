class NullState:

    def __init__(self,runtime,**kwargs):
        self.id = 'NULL'
        self.runtime = runtime
        self.kwargs = kwargs
        runtime.load_config_data(self)

    def tick(self, **kwargs):
        pass

    def on_active(self, **kwargs):
        pass

    def on_inactive(self, **kwargs):
        pass
