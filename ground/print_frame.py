from __future__ import print_function
import sys
import time


from ground_base import Frame, GroundBase

def handle_frame(frame):
    print("we got one", type(frame), frame.width, frame.height, frame.image.size, frame.image.getpixel((0,0)))



def main():
    ground = GroundBase()
    ground.parse_args()
    ground.register_frame_received(handle_frame)
    ground.wait_for_frames()


if __name__ == '__main__':
    main()