import json
import os
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
        os.makedirs(fn)
