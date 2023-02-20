import keyboard

class KeyboardCapture:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        self.enable = False

    def set_enable(self, enable):
        if self.enable == enable: return
        self.enable = enable
        if enable:
            keyboard.hook(self.keyboard_hook)
        else:
            keyboard.unhook(self.keyboard_hook)

    def keyboard_hook(self, kbevent):
        self.runtime.call_async('KEYBOARD_CAPTURE_EVENT', kwargs={'kbevent':kbevent})
