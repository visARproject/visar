import numpy as np

def find(key, _list, value):
    return filter(lambda o: key(o) == value)
