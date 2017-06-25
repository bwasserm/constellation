from __future__ import print_function
import json
import socket
import struct
import sys
import time

from PIL import Image
import serial

from ground_base import Frame, GroundBase, PY3

class NodeOutput(object):

    NUM_NODES = 16
    NODE_PORT = 17227  # DATE OF THE PARTY TO END ALL PARTIES
    BROADCAST_IP = "192.168.0.255"

    def __init__(self, patch, serial_name, down_res):
        self.patch = patch
        self.node_struct = struct.Struct(">BBBB")
        self.down_res = down_res

        if serial_name:
            self.serial = serial.Serial(serial_name)
            self.serial.open()
        else:
            self.serial = None

        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.out_sock.bind(('', 0))
        #self.out_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #self.out_sock.connect(('<broadcast>', self.NODE_PORT)) 

        self.packet_index = 0

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
        #self.out_sock.send(packet)
        for i in range (10):
            self.out_sock.sendto(packet, ("192.168.0.%d" % i, self.NODE_PORT))

    def reduce_image(self, frame, height, width):
        print("original", frame.height, frame.width)
        im_matrix = frame.image.load()
        #for row in range(frame.height):
        #    for col in range(frame.width):
        #        print(["%x" % c for c in im_matrix[col, row]], end='')
        #    print('')
        frame.image = frame.image.resize((width, height), resample=Image.ANTIALIAS)
        frame.width = frame.image.width
        frame.height = frame.image.height
        #print("smaller", frame.height, frame.width)
        #im_matrix = frame.image.load()
        #for row in range(frame.image.height):
        #    for col in range(frame.image.width):
        #        print(["%x" % c for c in im_matrix[col, row]], end='')
        #    print('')

    def map_pixels(self, image):
        width = image.width
        height = image.height
        nodes = {}

        pixels = image.load()
        self.packet_index += 1
        r = 255 if (self.packet_index % 8 >= 4) else 0
        g = 255 if (self.packet_index % 4 >= 2) else 0
        b = 255 if self.packet_index % 2 else 0

        # Map each node to a closes
        for node_id, relloc in self.patch.items():
            #x = int(relloc[0] * (height-1))
            #y = int(relloc[1] * (width-1))
            #nodes[node_id] = pixels[y, x]
            nodes[node_id] = (r, g, b)
            #print(node_id, relloc, x, y, nodes[node_id])

        return nodes

    def handle_frame(self, frame):
        print("we got one", frame.source, frame.image.size)
        im = frame.image.load()

        #self.reduce_image(frame, self.down_res[0], self.down_res[1])
        im_matrix = frame.image.load()
        #for row in range(frame.image.height):
        #    for col in range(frame.image.width):
        #        print(["%x" % c for c in im_matrix[col, row]], end='')
        #    print('')
        nodes = self.map_pixels(frame.image)
        packet = self.generate_packet(nodes)
        # print("generated packet", type(packet))
        #self.send_packet_serial(packet)
        self.send_packet_ip(packet)
        # print("<")
        # #print([hex(ord(c)) for c in list(packet)])
        # if PY3:
        #     print([chr(c) for c in packet[:7]])
        #     for node in range(self.NUM_NODES):
        #         print([hex(c) for c in packet[(7+node*4):(7+(node+1)*4)]])
        #     print([chr(c) for c in packet[-6:]])
        # else:
        #     print([c for c in packet[:7]])
        #     for node in range(self.NUM_NODES):
        #         print([hex(ord(c)) for c in packet[(7+node*4):(7+(node+1)*4)]])
        #     print([c for c in packet[-6:]])
        # print(">")


def main():
    ground = GroundBase()
    ground.argparse.add_argument("--patch_file",
                                 help="Path to file with node patch",
                                 default="./node_patch.json")
    ground.argparse.add_argument("--serial_port",
                                 help="Serial port to outpute path",
                                 default="")
    ground.argparse.add_argument("--downsample_res",
                                 help="Size to reduce image to before sending to nodes, XxY",
                                 default="10x10")
    ground.parse_args()

    patch = {}
    with open(ground.args.patch_file, "r") as patch_file:
        patch = {int(pix): loc for pix, loc in json.load(patch_file).items()}
    
    down_res = [int(val) for val in ground.args.downsample_res.split("x")]

    nodes = NodeOutput(patch, ground.args.serial_port, down_res)

    ground.register_frame_received(nodes.handle_frame)
    ground.wait_for_frames()


if __name__ == '__main__':
    main()