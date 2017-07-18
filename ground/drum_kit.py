
import random
import time

import numpy as np
import pygame
import pygame.midi

from ground_base import GroundBase

snare = ([0xAA], (128, 128, 0, 255))
tom1 = ([], (255, 0, 0, 255))
tom2 = ([], (0, 255, 0, 255))
tom3 = ([], (0, 0, 255, 255))
kick = ([], (255, 255, 255, 255))
ride = ([], (0, 128, 128, 255))
crash1 = ([], (128, 0, 128, 255))
highhat = ([], (0, 128, 128, 255))

drums = [snare, tom1, tom2, tom3, kick, ride, crash1, highhat]

def main():
    ground = GroundBase()
    ground.parse_args()

    nodes = dict()

    pygame.init()
    pygame.midi.init()
    pygame.fastevent.init()
    event_get = pygame.fastevent.get

    # list all midi devices
    for x in range( 0, pygame.midi.get_count() ):
         print pygame.midi.get_device_info(x)

    # open a specific midi device
    inp = pygame.midi.Input(1)
    print inp
 
    while True:
        if inp.poll():
            # no way to find number of messages in queue
            # so we just specify a high max value
            data = inp.read(1000)
            node = None
            if data[0][0][0] != 255:
                print [hex(byte) for byte in data[0][0]]
                for drum in drums:
                    if data[0][0][0] in drum[0]:
                        for _ in range(10):
                            node = random.choice(ground.active_nodes)
                            nodes[node] = drum[1]
            print nodes
            for node, color in nodes.iteritems():
                r, g, b = [c * 0.9 for c in color[:3]]
                nodes[node] = (r, g, b, 255)
            print nodes
            ground.set_nodes(nodes)
            time.sleep(0.01)

if __name__ == '__main__':
    main()