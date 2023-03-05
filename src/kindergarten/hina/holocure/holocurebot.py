import cv2
import numpy as np
import os

from . import state_classifier

from kindergarten import common

class HoloCureBot:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config

        self.enable = False
        
        state_classifier_config = list(filter(lambda i:i.id=='SCREEN_STATE',self.config.dlmodel_list))[0]
        self.state_classifier = state_classifier.StateClassifier(state_classifier_config)
        self.state_classifier.load()

        self.runtime.event_bus.add_listener('SCREEN_CAPTURE_IMG', self.on_SCREEN_CAPTURE_IMG)

        self.set_enable(getattr(self.config, 'holocurebot_enable', False))

    def set_enable(self, enable, **kwargs):
        self.enable = enable

    def on_SCREEN_CAPTURE_IMG(self, screen_shot, capture_sec, **kwargs):
        if not self.enable: return
    
        capture_ms = int(capture_sec*1000)
        screen_shot_1 = self.img_255_to_1(screen_shot)

        if self.is_img_blank(screen_shot_1):
            screen_state = 'BLANK'
        else:
            screen_state = cv2.resize(screen_shot_1, dsize=(128,128), interpolation=cv2.INTER_LINEAR)
            screen_state = np.expand_dims(screen_state, axis=0)
            screen_state, good = self.state_classifier.predict(screen_state)
            if not good:
                print(f'VNSAFEDIFR not good screen_state={screen_state}')
                fn_path = os.path.join(self.config.state_debug_path, screen_state, f'{capture_ms}.png')
                common.makedirs(os.path.dirname(fn_path))
                cv2.imwrite(fn_path, screen_shot)

        print(f'NAPUQJRBPH screen_state={screen_state}')

    def img_255_to_1(self, img):
        return (img.astype('float32')*2-255)/255

    def is_img_blank(self, img):
        img_max = img.max(axis=2)
        img_min = img.min(axis=2)
        img_diff = img_max-img_min
        img_diff2 = img_diff*img_diff
        img_abs2 = img_diff2.sum()
        abs2 = int(img_abs2)
        return abs2<=0.00025
