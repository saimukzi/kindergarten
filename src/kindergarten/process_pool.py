import os
import signal
import pygetwindow
import signal
import subprocess
import time
import wmi

from . import runtime as runtime_m

class ProcessPool:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        
        self.wmi = wmi.WMI()
        
        self.runtime.event_bus.add_listener('EXIT', self.on_EXIT)
    
    def init_process(self):
        self.kill_process(self.config.process_executable_path, signal.SIGTERM)
    
        good=False
        timeout = time.time()+10
        while (not good) and (time.time() < timeout):
            if self.check_process(self.config.process_executable_path): continue
            if self.check_window(self.config.window_title): continue
            good = True
            break
        if not good: return False
    
        popen_ret = subprocess.Popen(args=self.config.process)
    
        good=False
        timeout = time.time()+10
        while (not good) and (time.time() < timeout):
            if not self.check_process(self.config.process_executable_path): continue
            if not self.check_window(self.config.window_title): continue
            good = True
            break
        if not good: return False
    
        return True
    
    def on_EXIT(self, **kwargs):
        self.kill_process(self.config.process_executable_path, signal.SIGTERM)


    # def init_wmi(runtime):
    #     if not hasattr(runtime, 'wmi'):
    #         runtime.wmi = wmi.WMI()
    #     return runtime.wmi


    def kill_process(self, executable_path, s):
        w = self.wmi
        plist = w.Win32_Process()
        plist = list(filter(lambda p:p.ExecutablePath==executable_path,plist))
        for p in plist:
            os.kill(p.ProcessId, s)
        return len(plist)>0
    
    
    def check_process(self, executable_path):
        w = self.wmi
        plist = w.Win32_Process()
        plist = list(filter(lambda p:p.ExecutablePath==executable_path,plist))
        return len(plist)>0
    
    
    def check_window(self, title):
        wlist = pygetwindow.getWindowsWithTitle(title)
        return len(wlist) > 0
