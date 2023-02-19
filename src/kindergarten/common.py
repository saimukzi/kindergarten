import json
import types

def path_to_data(path):
    with open(path) as fin:
        return json.load(fin)


def path_to_namespace(path):
    with open(path, "r") as fin:
        return json.load(fin, object_hook= lambda x: types.SimpleNamespace(**x))

def not_func(func):
    def ret(b):
        return not b
    return ret
