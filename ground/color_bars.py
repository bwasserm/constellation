from pathlib import Path
import time

from PIL import Image

from ground_base import Frame, GroundBase

def main():
    ground = GroundBase()
    ground.parse_args()

    file_path = "SMPTE_Color_Bars.svg.png"
    im = Image.open(file_path)
    print(im)

    while True:
        width, height = im.size
        frame = Frame(source="color_bars", width=width, height=height, image=im)
        ground.send_frame(frame)
        time.sleep(1)

if __name__ == '__main__':
    main()