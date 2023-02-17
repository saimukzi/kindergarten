class StatePool:

    def __init__(self):
        self.id_to_state_dict = {}
        self.active_id = None
        self.active_state = None
        self.active_state_kwargs = None
        self.state_updated = False
        self.new_state = None
        self.new_state_kwargs = None

    def add_state(self, state):
        self.id_to_state_dict[state.id] = state

    def set_active(self, id, **kwargs):
        print(f'set_active: id={id}')
        self.active_id = id
        # self.new_state = self.id_to_state_dict.get(self.active_id, None)
        self.new_state = self.id_to_state_dict[self.active_id]
        self.new_state_kwargs = kwargs
        self.state_updated = True

    def tick(self, **kwargs):
        if self.state_updated:
            if self.active_state is not None:
                self.active_state.on_inactive(**kwargs)
            self.active_state = self.new_state
            self.active_state_kwargs = self.new_state_kwargs
            self.state_updated = False
            if self.active_state is not None:
                self.active_state.on_active(**kwargs, **self.active_state_kwargs)

        if self.active_state is None: return
        self.active_state.tick(**kwargs, **self.active_state_kwargs)
