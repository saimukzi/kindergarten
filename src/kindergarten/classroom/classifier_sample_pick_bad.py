import os

from kindergarten import common

class ClassifierSamplePickBadMain:

    def __init__(self, args):
        self.init_args = args
        self.config = common.read_config(self.init_args.config_file)
        self.classifier_config = list(filter(lambda i:i.id==self.init_args.classifier_id,self.config.dlmodel_list))[0]
        self.time = common.now()


    def run(self):
        work_path = os.path.join(self.config.tmp_path, 'classifier_sample_pick_bad', str(self.time))
        common.makedirs(work_path)
    
        sample_data_list_fn = os.path.join(self.config.tmp_path, 'sample_data_list.json')
        sample_data_list = common.path_to_data(sample_data_list_fn)
        
        sample_data_list = list(filter(lambda i:i['bad'], sample_data_list))

        label_list_path = os.path.join(self.classifier_config.model_path, 'label_list.json')
        label_list,label_id_name_list,label_count = common.path_to_label_list(label_list_path)
        label_id_to_name_dict = dict(label_id_name_list)

        for sample_data in sample_data_list:
            lid = sample_data['lid']
            ori_path = sample_data['path']
            lname = label_id_to_name_dict[lid]
            fn = os.path.split(ori_path)[1]
            tar_path = os.path.join(work_path,lname,fn)
            #print(f'ori_path={ori_path}, tar_path={tar_path}')
            if fn.startswith('f'): continue
            common.makedirs(os.path.dirname(tar_path))
            common.mv(ori_path, tar_path)

def run(args):
    main = ClassifierSamplePickBadMain(args)
    main.run()

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    parser.add_argument('classifier_id')
    args = parser.parse_args()

    run(args)
