from __future__ import print_function
import argparse
import socket
import struct
import sys
import time

from PIL import Image

PY3 = sys.version_info[0] == 3

MODE = "RGB"
PACKET_HEADER = b"CONSTELLATION"

#import node_output

def _bytes(src, enc="UTF-8"):
    if PY3:
        return bytes(src, enc)
    else:
        return str(src)

class Frame(object):
    def __init__(self, serialized="", source="", width=0, height=0, image=None):
        self.source = ""
        self.width = 0
        self.height = 0
        self.image = None

        if serialized:
            self.deserialize(serialized)
        else:
            self.source = source
            self.width = width
            self.height = height
            self.image = image if image is not None else Image.new(MODE, (self.width, self.height))

    def deserialize(self, serialized):
        try:
            source_len,  = struct.unpack(">I", serialized[:4])
            self.source, = struct.unpack_from(">{}s".format(source_len), serialized, offset=4)
            self.width, self.height, image_len = struct.unpack_from(">III", serialized, offset=(4+source_len))
            self.image = Image.frombuffer(MODE, (self.width, self.height), serialized[(4+source_len+12):], 'raw', MODE, 0, 1)
        except Exception as ex:
            print("Error {}: Unable to unpack".format(ex))
            raise

    def serialize(self):
        """ Convert the frame to a payload to send

            Returns:
                The packed string to transmit
        """
        try:
            image_bytes = self.image.tobytes()
            return struct.pack(">I{}sIII{}s".format(len(self.source), len(image_bytes)),
                               len(self.source),
                               _bytes(self.source, "UTF-8"),
                               self.width,
                               self.height,
                               len(image_bytes),
                               image_bytes)
        except Exception as ex:
            print(ex)
            raise
            print("Error {}: Unable to pack {}".format(ex, payload))
            return ""


class GroundBase(object):

    NUM_NODES = 16
    NODE_PORT = 17227  # DATE OF THE PARTY TO END ALL PARTIES
    BROADCAST_IP = "192.168.0.255"

    def __init__(self):
        self.args = None
        self.argparse = argparse.ArgumentParser(description="Constellation ground module")
        self.handler = None
        self.unify = True
        self.in_sock = None
        self.out_sock = None
        self.dest_addr = None
        self.in_buffer = b''
        self.out_counter = 0
        
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.out_sock.bind(('', 0))
        #self.out_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #self.out_sock.connect(('<broadcast>', self.NODE_PORT)) 

        # Set up command line arguments
        self.argparse.add_argument('--dest_addr',
                                   help="Address to send frame packets to, if no host provided default localhost",
                                   default="localhost:10001")
        self.argparse.add_argument('--listen_port', type=int,
                                   help="Port to listen for frame packets on",
                                   default=10002)

        self.nodes = dict()
        self.node_struct = struct.Struct(">BBBB")
        
    def parse_args(self):
        self.args = self.argparse.parse_args()

        # Create sockets
        self.in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Unpack destination address
        dest = self.args.dest_addr
        try:
            dest_port = int(dest)
            dest_host = "localhost"
        except ValueError:
            dest_host, dest_port = dest.split(":")
            dest_port = int(dest_port)
        self.dest_addr = (dest_host, dest_port)

    def register_frame_received(self, handler):
        """ Accepts a callback function to be run every time a frame is received
        
        The function will accept one argument, a frame to process
        """
        self.handler = handler
        
    def wait_for_frames(self):
        self.in_sock.bind(("0.0.0.0", self.args.listen_port))
        self.in_sock.settimeout(0.1)
        while True:
            try:
                data = self.in_sock.recv(4096)
            except socket.timeout:
                time.sleep(0.1)
                continue
            self.in_buffer += data
            try:
                #print("buffer size", len(self.in_buffer))
                start = self.in_buffer.index(PACKET_HEADER)
                if start > 0:
                    self.in_buffer = self.in_buffer[start:]
                counter, payload_size, = struct.unpack(">II", self.in_buffer[len(PACKET_HEADER):len(PACKET_HEADER)+8])
                # print("payload size", payload_size)
                if len(PACKET_HEADER) + 8 + payload_size <= len(self.in_buffer):
                    print("packet counter", counter)
                    payload = self.in_buffer[len(PACKET_HEADER) + 8:len(PACKET_HEADER) + 8 + payload_size]
                    frame = Frame(serialized=payload)
                    if self.handler:
                        # print('handling frame')
                        self.handler(frame)
                    else:
                        print("Got unhandled frame")
                        # print("Got unhandled frame {}".format(frame.width))
                    self.in_buffer = self.in_buffer[len(PACKET_HEADER) + 8 + payload_size:]
            except ValueError as err:  # haven't gotten new packet header
                pass # print(err)

    def _generate_packet(self, nodes):
        HEADER = b"CONSTEL"
        HEADER_SIZE = len(HEADER)
        FOOTER = b"LATION"
        packet = HEADER
        for node_id in range(self.NUM_NODES):
            if node_id in nodes:
                r, g, b, a = nodes[node_id]
                self.nodes[node_id] = nodes[node_id]
            else:
                # No new value for this node, use last value
                r, g, b, a = self.nodes.get(node_id, (0, 0, 0, 0))
            packet += self.node_struct.pack(r, g, b, a)
        packet += FOOTER
        return packet

    def _send_packet_ip(self, packet):
        #self.out_sock.send(packet)
        for i in range (10):
            self.out_sock.sendto(packet, ("192.168.0.%d" % i, self.NODE_PORT))

    def _map_pixels(self, image):
        width = image.width
        height = image.height
        nodes = {}

        pixels = image.load()
        #self.packet_index += 1
        #r = 255 if (self.packet_index % 8 >= 4) else 0
        #g = 255 if (self.packet_index % 4 >= 2) else 0
        #b = 255 if self.packet_index % 2 else 0

        # Map each node to a closes
        for node_id, relloc in self.patch.items():
            x = int(relloc[0] * (height-1))
            y = int(relloc[1] * (width-1))
            nodes[node_id] = pixels[y, x]
            #nodes[node_id] = (r, g, b)
            #print(node_id, relloc, x, y, nodes[node_id])

        return nodes

    def _reduce_image(self, frame, height, width):
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
        
    def set_nodes_frame(self, frame):
        self._reduce_image(frame, 10, 10)
        nodes = self._map_pixels(frame.image)
        packet = self._generate_packet(nodes)
        self._send_packet_ip(packet)

    def set_nodes(self, nodes):
        """ Write values out to the nodes

        Args:
            nodes: A dict of node IDs: tuple of (r, g, b, a)
        """
        packet = self._generate_packet(nodes)
        self._send_packet_ip(packet)