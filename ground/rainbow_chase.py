import time

import numpy as np

from ground_base import GroundBase

def color(degrees):
    r = 255 * ((np.sin(degrees / 180. * np.pi) + 1) / 2)
    g = 255 * ((np.sin((degrees + 120) / 180. * np.pi) + 1) / 2)
    b = 255 * ((np.sin((degrees + 240) / 180. * np.pi) + 1) / 2)
    a = 255
    return r, g, b, a

def main():
    ground = GroundBase()
    ground.parse_args()
    nodes = dict()
    degrees = 0

    frame_delay = 0.01
    while True:

        degrees += 1

        # Map each node to a closes
        for node_id in range(ground.NUM_NODES):
            nodes[node_id] = color(degrees + node_id * 15)
        ground.set_nodes(nodes)
        time.sleep(frame_delay)

if __name__ == '__main__':
    main()