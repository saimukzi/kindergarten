import time
import threading

#from types import SimpleNamespace

class Console:

    def __init__(self, runtime):
        self.runtime = runtime
        self.sn = {}
        self.sn['runtime'] = runtime
        self.line = None
        self.line_lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.run).start()
    
    def run(self):
        while self.runtime.running:
            line = input()
            with self.line_lock:
                self.line = line
            while self.runtime.running:
                time.sleep(0.1)
                with self.line_lock:
                    if self.line != None: continue

    def tick(self, _):
        #print('tick')
        if self.runtime.running:
            with self.line_lock:
                if self.line == None: return
                line = self.line
                self.line = None
            try:
                exec(line, self.sn)
            except Exception as e:
                print(str(e))
            except SystemExit as se:
                self.runtime.stop()
