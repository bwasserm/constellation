from __future__ import print_function
from pathlib import Path
import time

from PIL import Image

from ground_base import GroundBase

def main():
    ground = GroundBase()
    ground.parse_args()
    nodes = dict()
    packet_index = 0

    frame_delay = 0.1
    while True:
        packet_index += 1
        r = 255 if (packet_index % 8 >= 4) else 0
        g = 255 if (packet_index % 4 >= 2) else 0
        b = 255 if packet_index % 2 else 0
        a = 255

        # Map each node to a closes
        for node_id in range(6):
            nodes[node_id] = (r, g, b, a)
        ground.set_nodes(nodes)
        time.sleep(frame_delay)

if __name__ == '__main__':
    main()