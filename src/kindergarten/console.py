import code
import threading
import time

#from types import SimpleNamespace

PS1 = '>>> '
PS2 = '... '

class Console:

    def __init__(self, runtime):
        self.runtime = runtime
        self.sn = {}
        self.sn['r'] = runtime
        self.line = None
        self.console = code.InteractiveConsole(self.sn)
        self.more = False
        self.thread = None
        self.next_sec_ret = None

        self.runtime.event_bus.add_listener('CONSOLE',self.on_CONSOLE)

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
    
    def join(self):
        self.runtime.notify()
        self.thread.join()
    
    def run(self):
        try:
            while self.runtime.is_running():
                with self.runtime.main_lock:
                    if self.line is not None:
                        self.runtime.wait()
                        continue
                #print('SLIQHQFHDJ Console.input')
                line = input(PS2 if self.more else PS1)
                with self.runtime.main_lock:
                    self.line = line
                self.runtime.event_bus.call_async('CONSOLE')
        except:
            #print('ZUQXOXHDJI')
            self.runtime.stop()
            raise
        #print('XYBPBTWTME')

    def on_CONSOLE(self):
        #print('on_CONSOLE')
        if not self.runtime.is_running(): return
        with self.runtime.main_lock:
            if self.line is None: return
            try:
                self.more = self.console.push(self.line)
            except Exception as e:
                print(str(e))
            except SystemExit as se:
                self.runtime.stop()
            self.line = None
            self.next_sec_ret = None
            self.runtime.notify()
            # print('GVRMHHWGCC')
