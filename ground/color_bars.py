from __future__ import print_function
from pathlib import Path
import time

from PIL import Image

from ground_base import Frame, GroundBase

def main():
    ground = GroundBase()
    ground.parse_args()

    file_path = "color_bars.jpg"
    im = Image.open(file_path)
    print(im)

    width, height = im.size
    frame = Frame(source="color_bars", width=width, height=height, image=im)
    print(type(frame), frame.width, frame.height, frame.image.size, frame.image.getpixel((0,0)))
    while True:
        ground.send_frame(frame)
        #time.sleep(1)

if __name__ == '__main__':
    main()