from __future__ import print_function
import json
import struct
import sys
import time

from PIL import Image
import serial

from ground_base import Frame, GroundBase

class NodeOutput(object):

    NUM_NODES = 100

    def __init__(self, patch, serial_name, ip_addr):
        self.patch = patch
        if serial_name:
            self.serial = serial.Serial(serial_name)
            self.serial.open()
        else:
            self.serial = None
        self.node_struct = struct.Struct(">BBBB")

    def __del__(self):
        if self.serial:
            self.serial.close()

    def generate_packet(self, nodes):
        HEADER = b"CONSTEL"
        HEADER_SIZE = len(HEADER)
        FOOTER = b"LATION"
        packet = HEADER
        for node_id in range(self.NUM_NODES):
            if node_id in nodes:
                r, g, b = nodes[node_id]
                a = 0  # alpha channel
            else:
                r, g, b, a = 0, 0, 0, 0
            packet += self.node_struct.pack(r, g, b, a)
        packet += FOOTER
        return packet

    def send_packet_serial(self, packet):
        if self.serial:
            self.serial.write(packet)

    def send_packet_ip(self, packet):
        pass

    def reduce_image(self, frame, width, height):
        frame.image = frame.image.resize((width, height), resample=Image.BILINEAR)
        frame.width = width
        frame.height = height

    def map_pixels(self, image):
        width = image.width
        height = image.height
        nodes = {}

        pixels = image.load()

        # Map each node to a closes
        for node_id, relloc in self.patch.items():
            x = relloc[0] * (height-1)
            y = relloc[1] * (width-1)
            nodes[node_id] = pixels[x, y]

        return nodes

    def handle_frame(self, frame):
        print("we got one", frame.source, frame.image.size)
        self.reduce_image(frame, 10, 10)
        nodes = self.map_pixels(frame.image)
        packet = self.generate_packet(nodes)
        self.send_packet_serial(packet)
        self.send_packet_ip(packet)


def main():
    ground = GroundBase()
    ground.argparse.add_argument("--patch_file",
                                 help="Path to file with node patch",
                                 default="./node_patch.json")
    ground.argparse.add_argument("--serial_port",
                                 help="Serial port to outpute path")
    ground.parse_args()

    patch = {}
    with open(ground.args.patch_file, "r") as patch_file:
        patch = {int(pix): loc for pix, loc in json.load(patch_file).items()}
    
    nodes = NodeOutput(patch, ground.args.serial_port, ground.args.dest_addr)
    
    ground.register_frame_received(nodes.handle_frame)
    ground.wait_for_frames()


if __name__ == '__main__':
    main()