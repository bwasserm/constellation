from __future__ import print_function
from pathlib import Path
import time

from PIL import Image

from ground_base import Frame, GroundBase

def main():
    ground = GroundBase()
    ground.argparse.add_argument("--gif",
                                 help="Path to GIF file to load")
    ground.parse_args()

    file_path = ground.args.gif
    im = Image.open(file_path)
    palette = im.getpalette()
    pixels = im.load()
    width, height = im.size
    try:  # per the docs, duration may not be present
        frame_delay = im.info.duration / 1000  # value is in ms
    except AttributeError:
        frame_delay = 0.1
    temp_im = Image.new("RGB", im.size)
    while True:
        im.putpalette(palette)
        temp_im.paste(im)
        frame = Frame(source="gif:{}".format(file_path), width=width, height=height, image=temp_im)
        #print(pixels)
        ground.set_nodes_frame(frame)
        time.sleep(frame_delay)
        try:
            im.seek(im.tell() + 1)
        except EOFError:
            im.seek(0)

if __name__ == '__main__':
    main()