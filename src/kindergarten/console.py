import code
import time
import threading

#from types import SimpleNamespace

PS1 = '>>> '
PS2 = '... '

class Console:

    def __init__(self, runtime):
        self.runtime = runtime
        self.sn = {}
        self.sn['r'] = runtime
        self.line = None
        self.line_lock = threading.Condition()
        self.console = code.InteractiveConsole(self.sn)
        self.more = False
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.run).start()
    
    def join(self):
        with self.line_lock:
            self.line_lock.notify_all()
        self.thread.join()
    
    def run(self):
        while self.runtime.running:
            with self.line_lock:
                if self.runtime.running and self.line != None:
                    self.line_lock.wait()
                    continue
            line = input(PS2 if self.more else PS1)
            with self.line_lock:
                self.line = line

    def tick(self, _):
        #print('tick')
        if self.runtime.running:
            with self.line_lock:
                if self.line == None: return
                line = self.line
                self.line = None
                self.line_lock.notify_all()
            try:
                self.more = self.console.push(line)
            except Exception as e:
                print(str(e))
            except SystemExit as se:
                self.runtime.stop()
