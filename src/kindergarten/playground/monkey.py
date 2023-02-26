import keyboard
import random

from . import freq_timer

KEY_COMBO_LIST = [
    ['up'],
    ['down'],
    ['right'],
    ['left'],
    [],
]

class Monkey:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config

        self.enable = False
        self.last_combo = []

        self.freq_timer = freq_timer.FreqCallSyncTimer(runtime, runtime.config.fps, 'MONKEY_TICK')

        self.runtime.event_bus.add_listener('MONKEY_TICK', self.on_MONKEY_TICK)
        self.runtime.event_bus.add_listener('EXIT', self.on_EXIT)

    def set_enable(self, enable, **kwargs):
        self.enable = enable
        self.freq_timer.set_enable(enable=enable, **kwargs)
        self.do_combo([])

    def on_MONKEY_TICK(self, **kwargs):
        if not self.enable: return
        combo = random.choice(KEY_COMBO_LIST)
        self.do_combo(combo)

    def on_EXIT(self, **kwargs):
        self.do_combo([])

    def do_combo(self, combo):
        last_combo = set(self.last_combo)
        new_combo  = set(combo)

        for k in (last_combo-new_combo):
            keyboard.release(k)

        for k in (new_combo-last_combo):
            keyboard.press(k)
        
        self.last_combo = combo
