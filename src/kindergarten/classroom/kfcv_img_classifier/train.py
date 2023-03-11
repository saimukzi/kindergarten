import copy
import multiprocessing as mp
import os

from kindergarten import common

class KfcvImgClassifierTrainRuntime:

    def __init__(self, args):
        self.init_args = args
        self.config = common.read_config(self.init_args.config_file)
        self.classifier_config = list(filter(lambda i:i.id==self.init_args.classifier_id,self.config.dlmodel_list))[0]
        self.now = common.now()


    def run(self):
        self.mp(self.prepare_sample)

        common.reset_dir(self.classifier_config.model_path)
        common.copy(
            os.path.join(self.classifier_config.train_path, 'label_list.json'),
            os.path.join(self.classifier_config.model_path, 'label_list.json')
        )

        for i in range(self.classifier_config.fold_count):
            self.mp(self.train_fold, i, self.now)


    def prepare_sample(self):
        from . import prepare_sample
        prepare_sample.run(self.init_args)


    def train_fold(self, fold_id, now):
        from . import fold_train
        args = copy.deepcopy(self.init_args)
        args.fold_id = fold_id
        args.now = now
        fold_train.run(args)


    def mp(self, target, *args, **kwargs):
        p = mp.Process(target=target, args=args, kwargs=kwargs)
        p.start()
        p.join()
        if p.exitcode != 0:
            raise Exception(f'FQICPCTFLN mp exitcode={p.exitcode}')


def run(args):
    main = KfcvImgClassifierTrainRuntime(args)
    main.run()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    parser.add_argument('classifier_id')
    args = parser.parse_args()

    run(args)
