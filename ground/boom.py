from __future__ import print_function
from pathlib import Path
import time

from PIL import Image

from ground_base import GroundBase

def ready(node):
    codes = {}
    codes[node] = (73, 39, 109, 83)  # I'mS
    return codes

def arm(node):
    codes = {}
    codes[node] = (111, 114, 114, 121)  # orry
    return codes

def fire(node):
    codes = {}
    codes[node] = (68, 97, 118, 101)  # Dave
    return codes

def red(node):
    codes = {}
    codes[node] = (255, 0, 0, 255)  # Red
    return codes

def black(node):
    codes = {}
    codes[node] = (0, 0, 0, 255)  # Black
    return codes


def boom():
    ground = GroundBase()
    ground.parse_args()
    if len(ground.active_nodes) > 1:
        raise ValueError("Can only destroy one node at a time")
    node = ground.active_nodes[0]
    delay = 0.01
    while True:
        for i in range(1, 20):
            ground.set_nodes(black(node))
            time.sleep(1.0/i)
            ground.set_nodes(red(node))
            time.sleep(1.0/i)
        ground.set_nodes(ready(node))
        ground.set_nodes(arm(node))
        ground.set_nodes(fire(node))
        time.sleep(10)
        

if __name__ == '__main__':
    boom()