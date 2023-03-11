import math
import os
import tensorflow as tf

from kindergarten import common

from kindergarten.hina.holocure import state_classifier

class KicFoldTrainRuntime:

    def __init__(self, args):
        self.init_args = args
        self.config = common.read_config(self.init_args.config_file)
        self.classifier_config = list(filter(lambda i:i.id==self.init_args.classifier_id,self.config.dlmodel_list))[0]
        self.fold_id = self.init_args.fold_id
        self.now = self.init_args.now


    def run(self):
        # TODO
        self.classifier = state_classifier.StateClassifier(self.classifier_config)

        label_list_fn_path = os.path.join(self.classifier_config.train_path, 'label_list.json')
        label_list,label_id_name_list,label_count = common.path_to_label_list(label_list_fn_path)
        
        train_ds = None
        for i in range(self.classifier_config.fold_count):
            if i == self.fold_id: continue
            train_ds_fn = os.path.join(self.classifier_config.train_path, 'fold', str(i), 'img_lid.tfrecords')
            train_ds0 = tf.data.Dataset.load(train_ds_fn)
            if train_ds == None:
                train_ds = train_ds0
            else:
                train_ds = train_ds.concatenate(train_ds0)
        train_ds = train_ds.cache()

        valid_ds_fn = os.path.join(self.classifier_config.train_path, 'fold', str(self.fold_id), 'img_lid.tfrecords')
        valid_ds = tf.data.Dataset.load(valid_ds_fn).cache()
        valid_ds = valid_ds.batch(self.classifier_config.max_batch_size)

        train_sample_size = len(train_ds)
        max_batch_size = self.classifier_config.max_batch_size
        div_cnt = math.ceil(train_sample_size/max_batch_size)
        batch_size = math.ceil(train_sample_size/div_cnt)
        print(f'YLMGWCXGUS batch_size={batch_size}')

        train_ds = train_ds.batch(batch_size).prefetch(2)

        weight_fn = os.path.join(self.classifier_config.model_path, f'fold_weight_{self.fold_id}.hdf5')
        checkpointer = tf.keras.callbacks.ModelCheckpoint(filepath=weight_fn, verbose=1, save_best_only=True)
        
        log_dir = os.path.join(self.config.tmp_path, 'fit_log', str(self.now), str(self.fold_id))
        common.makedirs(log_dir)
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
        
        model = self.classifier.create_model(label_count)
        self.classifier.compile_model(model)

        model.fit(
            x=train_ds,
            validation_data=valid_ds,
            epochs = self.classifier_config.epochs, verbose=1,
            callbacks=[checkpointer, tensorboard_callback]
        )


def run(args):
    # print('CMTXJTURDB prepare_sample.run')
    runtime = KicFoldTrainRuntime(args)
    runtime.run()
