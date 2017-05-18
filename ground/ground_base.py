import argparse
import socket
import struct

from PIL import Image


MODE = "RGB"
PACKET_HEADER = b"CONSTELLATION"

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
            self.image = image if image is None else Image.new(MODE, (self.width, self.height))

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
            return struct.pack(">I{}sIII{}B".format(len(self.source), len(image_bytes)),
                               len(self.source),
                               bytes(self.source, "UTF-8"),
                               self.width,
                               self.height,
                               len(image_bytes),
                               *image_bytes)
        except Exception as ex:
            print(ex)
            raise
            print("Error {}: Unable to pack {}".format(ex, payload))
            return ""


class GroundBase(object):

    def __init__(self):
        self.args = None
        self.argparse = argparse.ArgumentParser(description="Constellation ground module")
        self.handler = None
        self.unify = True
        self.in_sock = None
        self.out_sock = None
        self.dest_addr = None
        self.in_buffer = b''
        
        # Set up command line arguments
        self.argparse.add_argument('dest_addr',
                                   help="Address to send frame packets to, if no host provided default localhost")
        self.argparse.add_argument('listen_port', type=int,
                                   help="Port to listen for frame packets on")
        
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
                continue
            self.in_buffer += data
            try:
                # print("buffer size", len(self.in_buffer))
                start = self.in_buffer.index(PACKET_HEADER)
                if start > 0:
                    self.in_buffer = self.in_buffer[start:]
                payload_size, = struct.unpack(">I", self.in_buffer[len(PACKET_HEADER):len(PACKET_HEADER)+4])
                # print("payload size", payload_size)
                if len(PACKET_HEADER) + 4 + payload_size <= len(self.in_buffer):
                    payload = self.in_buffer[len(PACKET_HEADER) + 4:len(PACKET_HEADER) + 4 + payload_size]
                    frame = Frame(serialized=payload)
                    if self.handler:
                        # print('handling frame')
                        self.handler(frame)
                    else:
                        print("Got unhandled frame")
                        # print("Got unhandled frame {}".format(frame.width))
                    self.in_buffer = self.in_buffer[len(PACKET_HEADER) + 4 + payload_size:]
            except ValueError as err:  # haven't gotten new packet header
                pass # print(err)
        
    def send_frame(self, frame):
        serialized = frame.serialize()
        if serialized:
            try:
                packet = PACKET_HEADER + bytes(struct.pack(">I", len(serialized))) + serialized
                print("Outgoing packet len: {}".format(len(packet)))
                CHUNK_SIZE = 4096
                while len(packet) > CHUNK_SIZE:
                    self.out_sock.sendto(packet[:CHUNK_SIZE], self.dest_addr)
                    packet = packet[CHUNK_SIZE:]
            except socket.error as err:
                pass  # Destination no longer exists, fail silently
                # print(err)