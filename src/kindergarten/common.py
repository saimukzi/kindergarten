import json

def path_to_data(path):
    with open(path) as fin:
        return json.load(fin)


def not_func(func):
    def ret(b):
        return not b
    return ret
