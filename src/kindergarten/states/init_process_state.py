import os
import pygetwindow
import signal
import subprocess
import wmi

from . import common_state
from . import null_state

def add_state(state_pool, runtime):
    state_pool.add_state(common_state.TransState('INIT_PROCESS','_INIT_PROCESS_0_SIGTERM',runtime))
    state_pool.add_state(common_state.FuncState('_INIT_PROCESS_0_SIGTERM', _INIT_PROCESS_0_SIGTERM, runtime))
    state_pool.add_state(_INIT_PROCESS_1_WAIT(runtime))
    state_pool.add_state(common_state.FuncState('_INIT_PROCESS_2_RUN', _INIT_PROCESS_2_RUN, runtime))
    state_pool.add_state(_INIT_PROCESS_3_WAIT(runtime))
    #state_pool.add_state(common_state.TransState('_INIT_PROCESS_9_END','DEAD',runtime))
    state_pool.add_state(common_state.TransState('_INIT_PROCESS_9_END','NULL',runtime))
    state_pool.add_state(null_state.NullState(runtime))


def _INIT_PROCESS_0_SIGTERM(runtime, **kwargs):
    kill_process(runtime.config_process_executable_path, signal.SIGTERM, runtime)
    runtime.state_pool.set_active('_INIT_PROCESS_1_WAIT')

def _INIT_PROCESS_1_WAIT(runtime):
    def f(runtime, **kwargs):
        if check_process(runtime.config_process_executable_path, runtime): return False
        if check_window(runtime.config_window_title): return False
        return True
    return common_state.WaitUntilState(
        '_INIT_PROCESS_1_WAIT',
        f, '_INIT_PROCESS_2_RUN',
        10, 'DEAD',
        runtime
    )


def _INIT_PROCESS_2_RUN(runtime, **kwargs):
    subprocess.Popen(args=runtime.config_process)
    runtime.state_pool.set_active('_INIT_PROCESS_3_WAIT')


def _INIT_PROCESS_3_WAIT(runtime):
    def f(runtime, **kwargs):
        if not check_process(runtime.config_process_executable_path, runtime): return False
        if not check_window(runtime.config_window_title): return False
        return True
    return common_state.WaitUntilState(
        '_INIT_PROCESS_3_WAIT',
        f, '_INIT_PROCESS_9_END',
        10, 'DEAD',
        runtime
    )

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


#def check_process_state_func(executable_path):
#    def ret(runtime, **kwargs):
#        return check_process(executable_path, runtime)
#    return ret
