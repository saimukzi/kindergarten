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
        self.line_lock = threading.Condition()
        self.console = code.InteractiveConsole(self.sn)
        self.more = False
        self.thread = None
        self.next_sec_ret = None

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
    
    def join(self):
        with self.line_lock:
            self.line_lock.notify_all()
        self.thread.join()
    
    def run(self):
        try:
            while self.runtime.running:
                with self.line_lock:
                    if self.runtime.running and self.line != None:
                        self.line_lock.wait()
                        continue
                if not self.runtime.running: break
                #print('SLIQHQFHDJ Console.input')
                line = input(PS2 if self.more else PS1)
                with self.line_lock:
                    self.line = line
                    self.next_sec_ret = time.time()
                self.runtime.timer_pool.notify()
        except:
            #print('ZUQXOXHDJI')
            self.runtime.stop()
            raise
        #print('XYBPBTWTME')

    def next_sec(self, now_sec, **kwargs):
        with self.line_lock:
            return self.next_sec_ret

    def tick(self, **kwargs):
        #print('tick')
        if self.runtime.running:
            with self.line_lock:
                if self.line == None: return
                #line = self.line
                #self.line = None
                #self.next_sec_ret = None
                #self.line_lock.notify_all()
                try:
                    self.more = self.console.push(self.line)
                except Exception as e:
                    print(str(e))
                except SystemExit as se:
                    # print('CFWESMBYHD: SystemExit detected')
                    self.runtime.stop()
                self.line = None
                self.next_sec_ret = None
                self.line_lock.notify_all()
                # print('GVRMHHWGCC')
