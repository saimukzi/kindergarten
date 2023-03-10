import keyboard
import pygetwindow
import traceback

class Hotkey:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        self.enable = False

        self.runtime.event_bus.add_listener('KEYBOARD_CAPTURE_EVENT', self.on_KEYBOARD_CAPTURE_EVENT)

        self.hotkey_tuple_list = self._get_hotkey_tuple_list()

        self.set_enable(getattr(self.config, 'hotkey_enable', False))


    def hk_f12(self):
        try:
            self.runtime.focus.focus()
        except pygetwindow.PyGetWindowException as pgwe:
            # focus on window in other screen will fail, just print the err
            traceback.print_exc()


    def hk_f11(self):
        self.runtime.screen_capture.set_enable(True)


    def hk_ctrl_f11(self):
        self.runtime.screen_capture.set_enable(False)


    def hk_f10(self):
        self.runtime.monkey.set_enable(True)


    def hk_ctrl_f10(self):
        self.runtime.monkey.set_enable(False)


    def hk_f9(self):
        self.runtime.screen_recorder.set_enable(True)


    def hk_ctrl_f9(self):
        self.runtime.screen_recorder.set_enable(False)


    def on_KEYBOARD_CAPTURE_EVENT(self, attr, **kwargs):
        if not self.enable: return
        getattr(self, attr)()


    def call_KEYBOARD_CAPTURE_EVENT(self, attr):
        self.runtime.event_bus.call_async('KEYBOARD_CAPTURE_EVENT', kwargs={'attr':attr})


    def set_enable(self, enable, **kwargs):
        # print(f'self.enable={self.enable}, enable={enable}')
        if self.enable == enable: return
        self.enable = enable
        if enable:
            for hotkey,attr in self.hotkey_tuple_list:
                keyboard.add_hotkey(hotkey, self.call_KEYBOARD_CAPTURE_EVENT, args=[attr])
        else:
            for hotkey,_ in self.hotkey_tuple_list:
                keyboard.remove_hotkey(hotkey)


    def _get_hotkey_tuple_list(self):
        attr_list = dir(self)
        ret_list = []
        for attr in attr_list:
            if not attr.startswith('hk_'): continue
            hk = attr[3:]
            hk = hk.replace('_','+')
            ret_list.append((hk, attr))
        # print(ret_list)
        return ret_list

