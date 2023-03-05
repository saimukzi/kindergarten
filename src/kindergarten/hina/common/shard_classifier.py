import numpy as np
import os
import tensorflow as tf

from kindergarten import common

# from kindergarten.hina.holocure import state_classifier_model_factory

class ShardClassifier():

    def __init__(self, classifier_config):
        self.classifier_config = classifier_config
        assert(self.classifier_config.type == 'classifier')
        # self.model_factory = state_classifier_model_factory.StateClassifierModelFactory()

    def load(self):
        label_list_path = os.path.join(self.classifier_config.model_path, 'label_list.json')
        self.label_list = common.path_to_data(label_list_path)

        self.model_list = []
        
        for shard_id in range(self.classifier_config.shard_count):
            weight_path = os.path.join(self.classifier_config.model_path, f'weight_{shard_id}.hdf5')
            #model = self.model_factory.create_model(len(self.label_list))
            model = self.create_model(len(self.label_list))
            model.load_weights(weight_path)
            self.model_list.append(model)
        
        self.score_np2_shape = (len(self.model_list),len(self.label_list))
        
        print(self.model_list[0].layers[0].dtype)

    def predict(self, x):
        score_np2 = list(map(lambda i:i(x),self.model_list))
        score_np2 = np.asarray(score_np2)
        score_np2 = score_np2.reshape(self.score_np2_shape)
        label_idx_np = score_np2.argmax(axis=1)
        label_k_np, label_c_np = np.unique(label_idx_np, return_counts=True)
        if len(label_k_np)==1:
            label_name = self.label_list[label_k_np[0]]
            return (label_name, True)
        else:
            score_np = score_np2.sum(axis=0)
            s_list = list(map(lambda i:-score_np[i], label_k_np))
            csk_list = list(zip(-label_c_np, s_list, label_k_np))
            csk_list = sorted(csk_list)
            label_name = self.label_list[csk_list[0][2]]
            return (label_name, False)
