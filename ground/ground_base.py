import argparse
import cStringIO
import json
import socket
import struct

from PIL import Image


MODE = "RGB"
PACKET_HEADER = b"CONSTELLATION"

class Frame(object):
    def __init__(self, serialized="", source="", width=0, height=0, image=None):
        if serialized:
            self.deserialize(serialized)
        else:
            self.source = source
            self.width = width
            self.height = height
            self.image = image if image is None else Image.new(MODE, (self.width, self.height))

    def deserialize(self, serialized):
        try:
            unpacked = json.loads(serialized)
            self.source = unpacked["source"]
            self.width = unpacked["width"]
            self.height = unpacked["height"]
            self.image = Image.frombuffer(MODE, (self.width, self.height), bytes(unpacked["image"]))
        except Exception as ex:
            print("Error {}: Unable to unpack {}".format(ex, serialized))

    def serialize(self):
        """ Convert the frame to a payload to send

            Returns:
                The jsonified string to transmit
        """
        payload = {"source": self.source,
                   "width": self.width,
                   "height": self.height,
                   "image" : list(self.image.tobytes())
                  }
        try:
            return json.dumps(payload)
        except Exception as ex:
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
        self.dest_addr = (dest_host, dest_port)

    def register_frame_received(self, handler):
        """ Accepts a callback function to be run every time a frame is received
        
        The function will accept one argument, a frame to process
        """
        self.handler = handler
        
    def wait_for_frames(self):
        self.in_sock.bind(("0.0.0.0", self.args.listen_port))
        while True:
            data = self.in_sock.recv(4096)
            self.in_buffer += data
            try:
                start = self.in_buffer.index(PACKET_HEADER)
                if start > 0:
                    self.in_buffer = self.in_buffer[start:]
                    payload_size = struct.unpack(">I", self.in_buffer[len(PACKET_HEADER)])
                    if len(PACKET_HEADER) + 4 + payload_size >= len(self.in_buffer):
                        payload = self.in_buffer[len(PACKET_HEADER) + 4:len(PACKET_HEADER) + 4 + payload_size]
                        frame = Frame(serialized=payload)
                        if self.handler:
                            self.handler(frame)
                        self.in_buffer = self.in_buffer[len(PACKET_HEADER) + 4 + payload_size:]
            except ValueError:  # haven't gotten new packet header
                pass
        
    def send_frame(self, frame):
        serialized = frame.serialize()
        if serialized:
            try:
                packet = PACKET_HEADER + struct.pack(">I", len(serialized)) + serialized
                self.out_sock.sendto(packet, self.dest_addr)
            except socket.error as err:
                pass  # Destination no longer exists, fail silently
                print(err)