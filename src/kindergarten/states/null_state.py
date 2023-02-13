class NullState:

    def __init__(self,runtime):
        self.id = 'NULL'
        self.runtime = runtime
        runtime.load_config_data(self)

    def tick(self, **kwargs):
        pass

    def on_active(self, **kwargs):
        pass

    def on_inactive(self, **kwargs):
        pass
