import signal

from . import common_state
from . import null_state
from . import init_process_state

def add_state(state_pool, runtime):
    state_pool.add_state(common_state.FuncState('DEAD', _DEAD, runtime))

def _DEAD(runtime, **kwargs):
    init_process_state.kill_process(runtime.config_process_executable_path, signal.SIGTERM, runtime)
    assert(False)
