import keyboard

class Hotkey:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        self.enable = False

        #self.runtime.event_bus.add_listener('KEYBOARD_CAPTURE_EVENT', self.on_KEYBOARD_CAPTURE_EVENT)

        self.hotkey_tuple_list = self._get_hotkey_tuple_list()

        self.set_enable(getattr(self.config, 'keyboard_capture_enable', False))


    def hk__f12(self):
        pass


    def hk__f11(self):
        pass


    def hk__ctrl_f11(self):
        pass


    def set_enable(self, enable, **kwargs):
        if self.enable == enable: return
        self.enable = enable
        if enable:
            for hotkey,f in self.hotkey_tuple_list:
                keyboard.add_hotkey(hotkey, f)
        else:
            for _,f in self.hotkey_tuple_list:
                keyboard.remove_hotkey(f)


    def _get_hotkey_tuple_list(self):
        attr_list = dir(self)
        ret_list = []
        for attr in attr_list:
            if not attr.startswith('hk__'): continue
            f = getattr(self,attr)
            hk = attr.split('__')[1]
            hk = hk.replace('_','+')
            ret_list.append((hk, f))
        # print(ret_list)
        return ret_list

