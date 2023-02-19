import os
import signal
import pygetwindow
import signal
import subprocess
import time
import wmi

from . import runtime as runtime_m

def init(runtime):
    runtime.event_bus.add_listener('EXIT', on_EXIT)

def init_process(runtime):
    kill_process(runtime.config.process_executable_path, signal.SIGTERM, runtime)

    good=False
    timeout = time.time()+10
    while (not good) and (time.time() < timeout):
        if check_process(runtime.config.process_executable_path, runtime): continue
        if check_window(runtime.config.window_title): continue
        good = True
        break
    if not good: return False

    popen_ret = subprocess.Popen(args=runtime.config.process)

    good=False
    timeout = time.time()+10
    while (not good) and (time.time() < timeout):
        if not check_process(runtime.config.process_executable_path, runtime): continue
        if not check_window(runtime.config.window_title): continue
        good = True
        break
    if not good: return False

    return True

def on_EXIT(**kwargs):
    runtime = runtime_m.instance
    kill_process(runtime.config.process_executable_path, signal.SIGTERM, runtime)

def init_wmi(runtime):
    if not hasattr(runtime, 'wmi'):
        runtime.wmi = wmi.WMI()
    return runtime.wmi


def kill_process(executable_path, s, runtime):
    w = init_wmi(runtime)
    plist = w.Win32_Process()
    plist = list(filter(lambda p:p.ExecutablePath==executable_path,plist))
    for p in plist:
        os.kill(p.ProcessId, s)
    return len(plist)>0


def check_process(executable_path, runtime):
    w = init_wmi(runtime)
    plist = w.Win32_Process()
    plist = list(filter(lambda p:p.ExecutablePath==executable_path,plist))
    return len(plist)>0


def check_window(title):
    wlist = pygetwindow.getWindowsWithTitle(title)
    return len(wlist) > 0
