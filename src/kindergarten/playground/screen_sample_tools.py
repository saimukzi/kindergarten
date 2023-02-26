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
        ret_list = os.listdir(scan_folder_path)
        ret_list = self.runtime.thread_pool.map(lambda i: os.path.join(scan_folder_path, i), ret_list)
        # ret_list = map(lambda i: os.path.join(scan_folder_path, i), ret_list)
        ret_list = list(ret_list)
        def is_blank(fn_path):
            img = cv2.imread(fn_path)
            img_max = img.max(2)
            img_min = img.min(2)
            img_diff = img_max-img_min
            img_diff2 = img_diff*img_diff
            img_abs2 = img_diff2.sum()
            abs2 = int(img_abs2)
            return abs2<=4
        ret_list = self.runtime.thread_pool.filter_uo(is_blank ,ret_list)
        ret_list = list(ret_list)
        return ret_list
