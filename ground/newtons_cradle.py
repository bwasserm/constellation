from __future__ import print_function
from pathlib import Path
import time

from PIL import Image

from ground_base import GroundBase

def set_color(_id, balloons):
    codes = {}
    for n in range(1, len(balloons)):
        if n == _id:
            codes[balloons[n]] = (0, 255, 0, 0)
        else:
            codes[balloons[n]] = (255, 0, 255, 0)
    return codes

def cradle():
    ground = GroundBase()
    ground.parse_args()
    delay = 0.5
    nodes = ground.active_nodes
    while True:
        for x in nodes:
            ground.set_nodes(set_color(x, nodes))
        time.sleep(delay)
        for x in nodes[::-1]:
            ground.set_nodes(set_color(x, nodes))
        time.sleep(delay)

if __name__ == '__main__':
    cradle()