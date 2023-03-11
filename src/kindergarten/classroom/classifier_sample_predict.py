import numpy as np
import os
import tensorflow as tf
import types

from kindergarten import common
from kindergarten.hina.holocure import state_classifier
from kindergarten.hina.common import fold_classifier

class ClassifierSamplePredictMain:

    def __init__(self, args):
        self.init_args = args
        self.config = common.read_config(self.init_args.config_file)
        self.classifier_config = list(filter(lambda i:i.id==self.init_args.classifier_id,self.config.dlmodel_list))[0]


    def run(self):
        self.classifier = state_classifier.StateClassifier(self.classifier_config)
        self.classifier.load()

        sample_ds = None
        sample_path_lid_list = []
        for i in range(self.classifier_config.fold_count):
            fold_path = os.path.join(self.classifier_config.train_path, 'fold', str(i))
        
            fold_sample_path_lid_list_path = os.path.join(fold_path, 'fold_sample_path_lid_list.json')
            fold_sample_path_lid_list = common.path_to_data(fold_sample_path_lid_list_path)
            sample_path_lid_list += fold_sample_path_lid_list
        
            fold_sample_ds_path = os.path.join(fold_path, 'img_lid.tfrecords')
            fold_sample_ds = tf.data.Dataset.load(fold_sample_ds_path)
            if sample_ds == None:
                sample_ds = fold_sample_ds
            else:
                sample_ds = sample_ds.concatenate(fold_sample_ds)
        sample_ds = sample_ds.cache()
        sample_ds = sample_ds.batch(self.classifier_config.max_batch_size)
        sample_ds = sample_ds.prefetch(2)
        
        sample_lid_np = list(map(lambda i:i[1],sample_path_lid_list))
        sample_lid_np = np.asarray(sample_lid_np) 

        score_np = list(map(lambda i:i.predict(sample_ds),self.classifier.model_list))
        score_np = np.asarray(score_np)

        self.score_np = score_np # fold, sample, label
        self.sample_lid_np = sample_lid_np

        self.cal_min_score_np()
        self.cal_bad_np()

        sample_data_list = list(enumerate(sample_path_lid_list))
        sample_data_list = map(
            lambda i:{
                'path':i[1][0],
                'lid':i[1][1],
                'score':self.min_score_np[i[0]].item(),
                'bad':self.bad_np[i[0]].item(),
            },
            sample_data_list)
        sample_data_list = list(sample_data_list)

        common.makedirs(self.config.tmp_path)
        common.data_to_path(sample_data_list, os.path.join(self.config.tmp_path, 'sample_data_list.json'))

    def cal_min_score_np(self):
        score_np0 = self.score_np # fold, sample, label
        sample_lid_np0 = self.sample_lid_np
        
        sample_lid_np0 = np.expand_dims(sample_lid_np0,axis=1)
        sample_lid_np0 = np.expand_dims(sample_lid_np0,axis=0)
        #print(sample_lid_np0.shape)
        
        # fold, sample
        score_np0 = np.take_along_axis(score_np0, sample_lid_np0, axis=2)
        #print(score_np0.shape)
        
        score_np0 = score_np0.reshape(score_np0.shape[:2])
        #print(score_np0.shape)
        
        # sample
        score_np0 = score_np0.min(axis=0)
        #print(f'score_np0.shape={score_np0.shape}')
        
        self.min_score_np = score_np0

    def cal_bad_np(self):
        score_np0 = self.score_np
        sample_lid_np0 = self.sample_lid_np
        
        # fold, sample
        predict_lid_np0 = score_np0.argmax(axis=2)
        #print(predict_lid_np0.shape)
        
        sample_lid_np0 = np.expand_dims(sample_lid_np0,axis=0)
        #print(sample_lid_np0.shape)
        
        lid_diff_np0 = predict_lid_np0 - sample_lid_np0
        #print(lid_diff_np0.shape)
        
        bad_np0 = lid_diff_np0.any(axis=0)
        #print(f'bad_np0.shape={bad_np0.shape}')
        
        self.bad_np = bad_np0


def run(args):
    main = ClassifierSamplePredictMain(args)
    main.run()

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    parser.add_argument('classifier_id')
    args = parser.parse_args()

    run(args)
