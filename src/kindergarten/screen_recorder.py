import PIL.Image
import os

class ScreenRecorder:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config
        self.runtime.event_bus.add_listener('SCREEN_CAPTURE_IMG', self.on_SCREEN_CAPTURE_IMG)
        self.enable = False
        self.game_state_id = None

    def set_game_state_id(self, game_state_id):
        self.game_state_id = game_state_id
        if game_state_id is None:
            self.output_folder_path = None
        else:
            self.output_folder_path = os.path.join(self.config.screen_record_path, game_state_id)
            if not os.path.isdir(self.output_folder_path):
                os.makedirs(self.output_folder_path)

    def stop(self):
        self.enable = False
        
    def set_enable(self, enable):
        self.enable = enable

    def on_SCREEN_CAPTURE_IMG(self, screen_shot, capture_sec, **kwargs):
        if not self.enable: return
        if self.output_folder_path is None: return
        capture_ts = int(capture_sec*1000)
        output_path = os.path.join(self.output_folder_path, f'{capture_ts}.png')
        im = PIL.Image.fromarray(screen_shot[:,:,[2,1,0]])
        im.save(output_path)
