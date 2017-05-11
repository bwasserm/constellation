import argparse
import json
import socket

class Frame(object):
	def __init__(self, serialized="", source="", width=0, height=0, buffer=[]):
		if serialized:
			try:
				unpacked = json.loads(serialized)
				self.source = unpacked["source"]
				self.width = unpacked["width"]
				self.height = unpacked["height"]
				self.unified = unpacked["rgb_frame"]
				self.separated = self._separate(self.unified)
				self._check_frame()
			except Exception as ex:
				print "Error {}: Unable to unpack {}".format(ex, serialized)
		else:
			self.source = source
			self.width = width
			self.height = height
			if len(buffer) == 3:
				self.separated = buffer
				self.unified = self._unify(buffer)
			else:
				self.unified = buffer
				self.separated = self._separate(buffer)
				
	def serialize(self, unified=True):
		""" Convert the frame to a payload to send
		
			Args:
				unified: True: Send the data from the unified frame, False: from the separated frame

			Returns:
				The jsonified string to transmit
		"""
		if unified:
			buffer = self.unified
		else:
			buffer = self._unify(self.separated)
		self._check_frame()
		payload = {"source": self.source,
				   "width": self.width,
				   "height": self.height,
				   "rgb_frame" = buffer
				  }
		try:
			return json.dumps(payload)
		except Exception as ex:
			print "Error {}: Unable to pack {}".format(ex, payload)
			return ""
	
	def _unify(self, separated):
		unified = [[[0, 0, 0] for j in self.width] for i in self.height]
		for color, row, col in (range(3), range(self.height), range(self.width)):
			unified[row][col][color] = separated[color][row][col]
		return unified
		
	def _separate(self, unified):
		separated = [[[0 for j in self.width] for i in self.height] for color in range(3)]
		for row, col, color in (range(self.height), range(self.width), range(3)):
			separated[color][row][col] = unified[row][col][color]
		return separated

	def _check_frame(self):
		assert len(self.unified) == self.height, "Height of unified frame doesn't match height: H={} Frame={}".format(self.height, self.unified)
		assert all([len(row) == self.width) for row in self.unified]), "Width of unified frame doesn't match width: W={} Frame={}".format(self.width, self.unified)
		assert all([[len(pixel) == 3 for pixel in row] for row in self.unified]), "Not all pixels 3 wide: {}".format(self.unified)
		
		assert len(self.separated) == 3
		assert all([len(color) == self.height for color in self.separated])
		assert all([[len(row) == self.width for row in color] for color in self.separated])


class GroundBase(object):

	def __init__(self):
		self.args = None
		self.argparse = argparse.ArgumentParser(description="Constellation ground module")
		self.handler = None
		self.unify = True
		
		# Set up command line arguments
		self.argparse.add_argument('dest_addr',
								   help="Address to send frame packets to, if no host provided default localhost")
		self.argparse.add_argument('listen_port', type=int,
								   help="Port to listen for frame packets on")
		
	def parse_args(self):
		self.args = self.argparse.parse_args()
		
	def register_frame_received(self, handler):
		""" Accepts a callback function to be run every time a frame is received
		
		The function will accept one argument, a frame to process
		"""
		self.handler = handler
		
	def wait_for_frames(self):
		pass
		
	def send_frame(self, frame):
		pass
		
	
