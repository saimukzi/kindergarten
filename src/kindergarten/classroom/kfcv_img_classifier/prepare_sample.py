import concurrent.futures
import cv2
import math
import numpy as np
import os
import random
import tensorflow as tf
import threading
import traceback

from kindergarten import common

class KicPrepareSampleRuntime:

    def __init__(self, args):
        self.init_args = args
        self.config = common.read_config(self.init_args.config_file)
        self.classifier_config = list(filter(lambda i:i.id==self.init_args.classifier_id,self.config.dlmodel_list))[0]

    def run(self):
        common.reset_dir(self.classifier_config.train_path)
        sample_folder_path = self.classifier_config.sample_path

        label_list,label_id_name_list,label_count = common.get_label_list(sample_folder_path)

        common.data_to_path(label_list, os.path.join(self.classifier_config.train_path, 'label_list.json'))

        sample_path_lid_list = common.get_sample_path_lid_list(sample_folder_path)
        random.shuffle(sample_path_lid_list)

        for i in range(self.classifier_config.fold_count):
            start = i * len(sample_path_lid_list) // 5
            end = (i+1) * len(sample_path_lid_list) // 5
            fold_sample_path_lid_list = sample_path_lid_list[start:end]
            fold_sample_path_lid_img_list = self.get_sample_path_lid_img_list(fold_sample_path_lid_list)
            random.shuffle(fold_sample_path_lid_img_list)
            fold_sample_path_lid_list = list(map(lambda i:i[:2], fold_sample_path_lid_img_list))
            fold_img_list_np = list(map(lambda i:i[2], fold_sample_path_lid_img_list))
            fold_img_list_np = np.array(fold_img_list_np)
            fold_lid_list_np = list(map(lambda i:i[1], fold_sample_path_lid_img_list))
            fold_lid_list_np = np.array(fold_lid_list_np)
            
            ds = tf.data.Dataset.from_tensor_slices((fold_img_list_np, fold_lid_list_np))
            
            fold_path = os.path.join(self.classifier_config.train_path, 'fold', str(i))
            common.makedirs(fold_path)

            common.data_to_path(fold_sample_path_lid_list, os.path.join(fold_path, 'fold_sample_path_lid_list.json'))
            ds.save(os.path.join(fold_path, 'img_lid.tfrecords'))

    def get_sample_path_lid_img_list(self, sample_path_lid_list):
        ret_list = []
        lock = threading.Lock()
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for img_path, lid in sample_path_lid_list:
                f = executor.submit(self.load_img_append, img_path, lid, ret_list, lock)
                futures.append(f)
            concurrent.futures.wait(futures)
        return ret_list

    def load_img_append(self, img_path, lid, ret_list, lock):
        try:
            img = self.load_img(img_path, lock)
            with lock:
                ret_list.append((img_path, lid, img))
        except:
            traceback.print_exc()
        return True

    def load_img(self, fn, lock):
        img = cv2.imread(fn)
        img = (img.astype('float32')*2-255)/255
        img = cv2.resize(img, dsize=(128,128), interpolation=cv2.INTER_LINEAR)
        return img

def run(args):
    # print('CMTXJTURDB prepare_sample.run')
    runtime = KicPrepareSampleRuntime(args)
    runtime.run()
