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
    print(im, im.getpixel((0,0)))

    width, height = im.size
    frame = Frame(source="color_bars", width=width, height=height, image=im)
    print(type(frame.image), frame.width, frame.height, frame.image.size, frame.image.getpixel((0,0)))
    while True:
        ground.send_frame(frame)
        time.sleep(1)
        #break

if __name__ == '__main__':
    main()