import cv2
import numpy as np
import os

class ScreenSampleTools:

    def __init__(self, runtime):
        self.runtime = runtime
        self.config = runtime.config

    def get_blank_sample_filename_list(self):
        ret_list = []
        scan_folder_path = os.path.join(self.config.screen_record_path, '_')
        if not os.path.isdir(scan_folder_path): return []
        fn_list = os.listdir(scan_folder_path)
        for fn in fn_list:
            fn_path = os.path.join(scan_folder_path, fn)
            img = cv2.imread(fn_path)
            img_max = img.max(2)
            img_min = img.min(2)
            img_diff = img_max-img_min
            img_diff2 = img_diff*img_diff
            img_abs2 = img_diff2.sum()
            abs2 = int(img_abs2)
            if abs2 > 4: continue
            ret_list.append(fn_path)
        return ret_list
