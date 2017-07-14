from __future__ import print_function
from pathlib import Path
import time

from PIL import Image

from ground_base import GroundBase

def set_color(_id):
    codes = {}
    balloons = [0, 1, 3, 2]
    for n in [1, 2, 3]:
        if n == _id:
            codes[balloons[n]] = (0, 255, 0, 0)
        else:
            codes[balloons[n]] = (255, 0, 255, 0)
    return codes

def cradle():
    ground = GroundBase()
    ground.parse_args()
    delay = 0.5
    while True:
        for x in range(1, 4):
            ground.set_nodes(set_color(x))
        time.sleep(delay)
        for x in range(3, 1, -1):
            ground.set_nodes(set_color(x))
        time.sleep(delay)

if __name__ == '__main__':
    cradle()