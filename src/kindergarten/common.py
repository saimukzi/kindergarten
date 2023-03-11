import json
import os
import shutil
import time
import types

INF = float('inf')

def path_to_data(path):
    with open(path) as fin:
        return json.load(fin)


def path_to_namespace(path):
    with open(path, "r") as fin:
        return json.load(fin, object_hook= lambda x: types.SimpleNamespace(**x))


def data_to_path(data, fn):
    with open(fn, 'w') as fout:
        json.dump(data, fout, sort_keys=True, indent=2)
        fout.write('\n')


def read_config(path):
    config_data = path_to_data(path)
    config_data = _read_config(config_data)
    return config_data


def _read_config(data):
    if data is None:
        return data
    if type(data) == str:
        return data
    if type(data) == int:
        return data
    if type(data) == bool:
        return data
    if type(data) == list:
        data = map(_read_config,data)
        data = list(data)
        return data
    if type(data) == dict:
        ret = types.SimpleNamespace()
        for k,v in data.items():
            if k.endswith('./'):
                if os.sep != '/': continue
                k=k[:-2]
            if k.endswith('.\\'):
                if os.sep != '\\': continue
                k=k[:-2]
            setattr(ret, k, _read_config(v))
        return ret
    assert(False)

def not_func(func):
    def ret(b):
        return not b
    return ret


def makedirs(fn):
    if not os.path.isdir(fn):
        os.makedirs(fn)\

def rmdir(fn):
    shutil.rmtree(fn, ignore_errors=True)

def reset_dir(fn):
    rmdir(fn)
    makedirs(fn)

# label_list,label_id_name_list,label_count = common.get_label_list(path)
def get_label_list(sample_path):
    label_list = os.listdir(sample_path)
    label_list = sorted(label_list)
    label_id_name_list = list(enumerate(label_list))
    label_count = len(label_list)
    return label_list, label_id_name_list, label_count


# label_list,label_id_name_list,label_count = common.path_to_label_list(path)
def path_to_label_list(path):
    label_list = path_to_data(path)
    label_id_name_list = list(enumerate(label_list))
    label_count = len(label_list)
    return label_list, label_id_name_list, label_count


def get_sample_path_lid_list(sample_folder_path):
    #print(f'DKRYFTPYZR sample_folder_path={sample_folder_path}')
    label_list,label_id_name_list,label_count = get_label_list(sample_folder_path)

    ret_list = []
    for lid, lname in label_id_name_list:
        #print(f'ORBZJSBMBY sample_folder_path={sample_folder_path}, lname={lname}')
        label_path = os.path.join(sample_folder_path, lname)
        #print(f'FCNGQTPLVV label_path={label_path}')
        sample_filename_list = os.listdir(label_path)
        for sample_filename in sample_filename_list:
            sample_path = os.path.join(label_path, sample_filename)
            ret_list.append((sample_path, lid))
    return ret_list


def now():
    return int(time.time()*1000)


mv = shutil.move
copy = shutil.copyfile
