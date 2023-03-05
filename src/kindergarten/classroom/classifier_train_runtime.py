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

#from kindergarten.hina.holocure import state_classifier_model_factory
from kindergarten.hina.holocure import state_classifier

class ClassifierTrainRuntime:

    def __init__(self, args):
        self.init_args = args
        self.config = common.read_config(self.init_args.config_file)

        self.classifier_config = list(filter(lambda i:i.id==self.init_args.classifier_id,self.config.dlmodel_list))[0]
        #self.model_factory = state_classifier_model_factory.StateClassifierModelFactory()
        self.classifier = state_classifier.StateClassifier(self.classifier_config)


    def run(self):
        #tmp = self.config.dlmodel_list
        #tmp = filter(lambda i:i.id==self.init_args.classifier_id, tmp)
        #tmp = list(tmp)
        #assert(len(tmp)==1)
        #tmp = tmp[0]
        #self.classifier_config = tmp
        #assert(self.classifier_config.type == 'classifier')

        common.makedirs(os.path.dirname(self.classifier_config.model_path))
        
        sample_folder_path = self.classifier_config.sample_path

        tmp = os.listdir(sample_folder_path)
        tmp = sorted(tmp)
        self.label_list = tmp
        self.label_id_name_list = enumerate(self.label_list)
        state_count = len(self.label_list)

        common.data_to_path(self.label_list, os.path.join(self.classifier_config.model_path, 'label_list.json'))

        tmp = []
        for ssid, ssname in self.label_id_name_list:
            ss_path = os.path.join(sample_folder_path, ssname)
            sample_filename_list = os.listdir(ss_path)
            for sample_filename in sample_filename_list:
                sample_path = os.path.join(ss_path, sample_filename)
                tmp.append((sample_path, ssid))
        self.sample_path_ssid_list = tmp
        random.shuffle(self.sample_path_ssid_list)
        #self.sample_path_ssid_list = self.sample_path_ssid_list[:10]

        sample_count = len(self.sample_path_ssid_list)
        
        self.sample_img_ssid_list = self.get_sample_img_ssid_list(self.sample_path_ssid_list)

        for shard_id in range(self.classifier_config.shard_count):
            print(f'UQGADEJBUS shard_id={shard_id}')
            weight_fn = os.path.join(self.classifier_config.model_path, f'weight_{shard_id}.hdf5')
            #weight_fn = self.classifier_config.weight_file_path_format.format(shard_id=shard_id)
            checkpointer = tf.keras.callbacks.ModelCheckpoint(filepath=weight_fn, verbose=1, save_best_only=True)
        
            valid_start_idx = sample_count*shard_id // self.classifier_config.shard_count
            valid_end_idx = sample_count*(shard_id+1) // self.classifier_config.shard_count
            print(f'DWDESYAHLV valid_start_idx={valid_start_idx}, valid_end_idx={valid_end_idx}')
            train_sample_img_ssid_list = self.sample_img_ssid_list[:valid_start_idx]+self.sample_img_ssid_list[valid_end_idx:]
            valid_sample_img_ssid_list = self.sample_img_ssid_list[valid_start_idx:valid_end_idx]
            random.shuffle(train_sample_img_ssid_list)
            
            train_sample_size = len(train_sample_img_ssid_list)
            print(f'LNWCFABELZ train_sample_size={train_sample_size}')
            
            train_imgs, train_labels = zip(*train_sample_img_ssid_list)
            valid_imgs, valid_labels = zip(*valid_sample_img_ssid_list)
            train_imgs = np.array(train_imgs)
            train_labels = np.array(train_labels)
            valid_imgs = np.array(valid_imgs)
            valid_labels = np.array(valid_labels)
            
            max_batch_size = self.classifier_config.max_batch_size
            div_cnt = math.ceil(train_sample_size/max_batch_size)
            batch_size = math.ceil(train_sample_size/div_cnt)
            print(f'YLMGWCXGUS batch_size={batch_size}')

            model = self.classifier.create_model(state_count)
            self.classifier.compile_model(model)
            model.fit(
                train_imgs, train_labels,
                validation_data=(valid_imgs, valid_labels),
                epochs = self.classifier_config.epochs, batch_size=batch_size, verbose=1,
                callbacks=[checkpointer]
            )

    def get_sample_img_ssid_list(self, sample_path_ssid_list):
        print(f'SCVZPXPJRR get_sample_img_ssid_list')
        ret_list = []
        lock = threading.Lock()
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for img_path, ssid in sample_path_ssid_list:
                f = executor.submit(self.load_img_append, img_path, ssid, ret_list, lock)
                futures.append(f)
            #print('TUIDSIIIAI')
            concurrent.futures.wait(futures)
            #for f in futures:
            #    f.result()
        print('RKILMAJAWB')
        return ret_list

    def load_img_append(self, img_path, ssid, ret_list, lock):
        #print(f'EOQCCPKRAP load_img_append {img_path} START')
        try:
            img = self.load_img(img_path, lock)
            with lock:
                ret_list.append((img, ssid))
            #print(f'WONYKLFAZS load_img_append {img_path} END')
        except:
            traceback.print_exc()
        return True

    def load_img(self, fn, lock):
        #print(f'TTRDMNNGGH load_img {fn} START')
        img = cv2.imread(fn)
        img = (img.astype('float32')*2-255)/255
        img = cv2.resize(img, dsize=(128,128), interpolation=cv2.INTER_LINEAR)
        #print(f'ELAMJDYXZR load_img {fn} END')
        return img

#    def create_mode(self, state_count):
#        INPUT_SHAPE = (128,128,3)
#        model = tf.keras.Sequential([
#            tf.keras.layers.GaussianNoise(stddev=0.2, input_shape=INPUT_SHAPE),
#            tf.keras.layers.Conv2D(filters=3, kernel_size=1, padding='valid', activation='elu'),
#            tf.keras.layers.Conv2D(filters=8, kernel_size=5, padding='valid', activation='elu'),
#            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
#            tf.keras.layers.MaxPooling2D(pool_size=4),
#            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
#            tf.keras.layers.Conv2D(filters=8, kernel_size=4, padding='valid', activation='elu'),
#            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
#            tf.keras.layers.MaxPooling2D(pool_size=4),
#            tf.keras.layers.Conv2D(filters=8, kernel_size=1, padding='valid', activation='elu'),
#            tf.keras.layers.Conv2D(filters=32, kernel_size=7, padding='valid', activation='elu'),
#            tf.keras.layers.Flatten(activity_regularizer=tf.keras.regularizers.L2(0.001)),
#            #tf.keras.layers.Flatten(),
#            #tf.keras.layers.BatchNormalization(),
#            tf.keras.layers.Dense(32, activation='elu'),
#            tf.keras.layers.Dropout(0.5),
#            tf.keras.layers.Dense(state_count, activity_regularizer=tf.keras.regularizers.L1(0.001)),
#            #tf.keras.layers.Dense(state_count),
#            tf.keras.layers.Softmax(),
#        ])
#        model.compile(optimizer='adam',
#                      loss=tf.keras.losses.SparseCategoricalCrossentropy(),
#                      metrics=['accuracy'])
#        return model


instance = None

def run(args):
    global instance
    instance = ClassifierTrainRuntime(args)
    instance.run()
